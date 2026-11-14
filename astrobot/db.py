from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time

import aiosqlite

from .core import LANGS

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, lang TEXT NOT NULL DEFAULT '',
 birth TEXT, sign TEXT, clock TEXT NOT NULL DEFAULT '08:00', zone TEXT NOT NULL DEFAULT 'Asia/Tehran',
 subscribed INTEGER NOT NULL DEFAULT 0, blocked INTEGER NOT NULL DEFAULT 0,
 next_due REAL NOT NULL DEFAULT 0, referred_by INTEGER, source TEXT,
 created REAL NOT NULL, last_seen REAL NOT NULL);
CREATE INDEX IF NOT EXISTS due_users ON users(subscribed,blocked,next_due);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS states(user_id INTEGER PRIMARY KEY, value TEXT NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY, value TEXT NOT NULL, expires REAL NOT NULL);
CREATE INDEX IF NOT EXISTS cache_exp ON cache(expires);
CREATE TABLE IF NOT EXISTS jobs(
 id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, title TEXT NOT NULL, hours INTEGER NOT NULL,
 kind TEXT NOT NULL, lang TEXT NOT NULL, sign TEXT NOT NULL,
 enabled INTEGER NOT NULL DEFAULT 1, next_due REAL NOT NULL, retry_at REAL NOT NULL DEFAULT 0,
 last_error TEXT NOT NULL DEFAULT '');
CREATE INDEX IF NOT EXISTS due_jobs ON jobs(enabled,next_due,retry_at);
CREATE TABLE IF NOT EXISTS deliveries(
 scope TEXT NOT NULL, slot TEXT NOT NULL, part INTEGER NOT NULL,
 sent REAL NOT NULL, PRIMARY KEY(scope,slot,part));
CREATE TABLE IF NOT EXISTS annual(
 year INTEGER NOT NULL, sign TEXT NOT NULL, lang TEXT NOT NULL, text TEXT NOT NULL,
 PRIMARY KEY(year,sign,lang));
CREATE TABLE IF NOT EXISTS moods(user_id INTEGER NOT NULL, day TEXT NOT NULL, score INTEGER NOT NULL,
 PRIMARY KEY(user_id,day));
CREATE TABLE IF NOT EXISTS broadcasts(
 id INTEGER PRIMARY KEY, text TEXT NOT NULL, cursor INTEGER NOT NULL DEFAULT 0,
 max_user_id INTEGER NOT NULL, sent INTEGER NOT NULL DEFAULT 0, failed INTEGER NOT NULL DEFAULT 0,
 enabled INTEGER NOT NULL DEFAULT 1, created REAL NOT NULL);
"""


class DB:
    async def open(self, path):
        self.conn = await aiosqlite.connect(path, isolation_level=None)
        self.conn.row_factory = aiosqlite.Row
        self.write_lock = asyncio.Lock()
        await self.conn.executescript(SCHEMA)
        from .migrations import upgrade

        await upgrade(self.conn)
        return self

    async def close(self):
        await self.conn.close()

    async def execute(self, sql, args=()):
        async with self.write_lock:
            async with self.conn.execute(sql, args) as cursor:
                return cursor.lastrowid

    async def one(self, sql, args=()):
        async with self.write_lock:
            async with self.conn.execute(sql, args) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def all(self, sql, args=()):
        async with self.write_lock:
            async with self.conn.execute(sql, args) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def batch(self, statements):
        async with self.write_lock:
            await self.conn.execute("BEGIN IMMEDIATE")
            try:
                result = []
                for sql, args in statements:
                    async with self.conn.execute(sql, args) as cursor:
                        result.append((cursor.lastrowid, cursor.rowcount))
                await self.conn.commit()
                return result
            except BaseException:
                await self.conn.rollback()
                raise

    async def abuse_token(self, uid):
        seed = await self.setting("anti_abuse_seed")
        return hmac.new(seed.encode(), str(uid).encode(), hashlib.sha256).hexdigest()

    async def user(self, uid):
        return await self.one("SELECT * FROM users WHERE id=?", (uid,))

    async def touch(self, uid, name, lang="", referred_by=None, source=None, identity=None):
        await self.execute(
            """INSERT INTO users(id,name,lang,referred_by,source,created,last_seen,language_selected)
          VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,
          blocked=0,last_seen=excluded.last_seen""",
            (uid, name[:128], lang, referred_by, source, time.time(), time.time(), int(lang in LANGS)),
        )

        if identity is not None:
            await self.execute(
                "UPDATE users SET last_name=?,username=?,telegram_lang=?,premium=? WHERE id=?",
                (
                    str(identity.get("last_name") or "")[:128],
                    str(identity.get("username") or "")[:64],
                    str(identity.get("telegram_lang") or "")[:16],
                    int(bool(identity.get("premium"))),
                    uid,
                ),
            )

    async def setting(self, key, default=None):
        row = await self.one("SELECT value FROM settings WHERE key=?", (key,))
        return json.loads(row["value"]) if row else default

    async def set(self, key, value):
        await self.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, json.dumps(value, ensure_ascii=False)))

    async def state(self, uid):
        row = await self.one("SELECT value FROM states WHERE user_id=? AND expires>?", (uid, time.time()))
        return json.loads(row["value"]) if row else None

    async def set_state(self, uid, value=None):
        if value is None:
            await self.execute("DELETE FROM states WHERE user_id=?", (uid,))
        else:
            await self.execute(
                "INSERT OR REPLACE INTO states VALUES(?,?,?)", (uid, json.dumps(value), time.time() + 1800)
            )

    async def cached(self, key):
        row = await self.one("SELECT value FROM cache WHERE key=? AND expires>?", (key, time.time()))
        return json.loads(row["value"]) if row else None

    async def cache(self, key, value, ttl=3600):
        await self.execute("INSERT OR REPLACE INTO cache VALUES(?,?,?)", (key, json.dumps(value), time.time() + ttl))

    async def sent(self, scope, slot, part=0):
        return bool(await self.one("SELECT 1 FROM deliveries WHERE scope=? AND slot=? AND part=?", (scope, slot, part)))

    async def mark(self, scope, slot, part=0):
        await self.execute("INSERT OR IGNORE INTO deliveries VALUES(?,?,?,?)", (scope, slot, part, time.time()))

    async def forget(self, uid):
        # Autocommit statements contain no intervening awaits outside this connection;
        # per-user handler lock prevents profile recreation during deletion.
        await self.execute("DELETE FROM moods WHERE user_id=?", (uid,))
        await self.execute("DELETE FROM states WHERE user_id=?", (uid,))
        await self.execute("DELETE FROM deliveries WHERE scope=?", (f"user:{uid}",))
        await self.execute("DELETE FROM deliveries WHERE scope LIKE 'broadcast:%' AND slot=?", (str(uid),))
        await self.execute("UPDATE users SET referred_by=NULL WHERE referred_by=?", (uid,))
        await self.execute(
            "DELETE FROM cache WHERE key LIKE ? OR key LIKE ? OR key LIKE ? OR key LIKE ?",
            (f"natal:{uid}:%", f"tarot:{uid}:%", f"personal-payload:{uid}:%", f"spread:{uid}:%"),
        )
        logs = await self.all("SELECT chat_id,message_id FROM log_messages WHERE user_id=?", (uid,))
        for item in logs:
            await self.execute(
                "INSERT INTO outbox(user_id,kind,chat_id,payload,created) VALUES(NULL,?,?,?,?)",
                ("delete", item["chat_id"], json.dumps({"message_id": item["message_id"]}), time.time()),
            )
        await self.execute("DELETE FROM users WHERE id=?", (uid,))

    async def cleanup(self):
        now = time.time()
        await self.execute("DELETE FROM cache WHERE expires<?", (now,))
        await self.execute("DELETE FROM states WHERE expires<?", (now,))
        await self.execute("DELETE FROM deliveries WHERE sent<?", (now - 86400 * 45,))
        await self.execute("DELETE FROM events WHERE created<?", (now - 86400 * 90,))
        await self.execute("DELETE FROM log_messages WHERE created<?", (now - 86400 * 30,))
        await self.execute("DELETE FROM outbox WHERE attempts>=10 OR created<?", (now - 86400 * 7,))
