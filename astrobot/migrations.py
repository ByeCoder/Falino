"""Forward-only, idempotent upgrade from the original Astra schema."""

import json
import secrets
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .core import LANGS

COLUMNS = {
    "language_selected": "INTEGER NOT NULL DEFAULT 0",
    "nickname": "TEXT NOT NULL DEFAULT ''",
    "birth_calendar": "TEXT NOT NULL DEFAULT 'g'",
    "last_name": "TEXT NOT NULL DEFAULT ''",
    "username": "TEXT NOT NULL DEFAULT ''",
    "telegram_lang": "TEXT NOT NULL DEFAULT ''",
    "premium": "INTEGER NOT NULL DEFAULT 0",
    "banned": "INTEGER NOT NULL DEFAULT 0",
    "points": "INTEGER NOT NULL DEFAULT 0",
    "streak": "INTEGER NOT NULL DEFAULT 0",
    "best_streak": "INTEGER NOT NULL DEFAULT 0",
    "streak_day": "TEXT",
    "ref_rewarded": "INTEGER NOT NULL DEFAULT 0",
}
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,kind TEXT NOT NULL,detail TEXT NOT NULL DEFAULT '',
 sign TEXT NOT NULL DEFAULT '',source TEXT NOT NULL DEFAULT '',created REAL NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL);
CREATE INDEX IF NOT EXISTS events_time ON events(created,kind);
CREATE INDEX IF NOT EXISTS events_user ON events(user_id,created);
CREATE TABLE IF NOT EXISTS metric_days(
 day TEXT NOT NULL,kind TEXT NOT NULL,detail TEXT NOT NULL,count INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(day,kind,detail));
CREATE TABLE IF NOT EXISTS active_days(
 day TEXT NOT NULL,user_id INTEGER NOT NULL,PRIMARY KEY(day,user_id),
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS history(
 id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,kind TEXT NOT NULL,sign TEXT NOT NULL DEFAULT '',
 lang TEXT NOT NULL,cards TEXT NOT NULL,delivered INTEGER NOT NULL DEFAULT 0,favorite INTEGER NOT NULL DEFAULT 0,rating INTEGER,
 created REAL NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS history_user ON history(user_id,id DESC);
CREATE TABLE IF NOT EXISTS card_collection(
 user_id INTEGER NOT NULL,card TEXT NOT NULL,created REAL NOT NULL,PRIMARY KEY(user_id,card),
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS reward_days(
 user_id INTEGER NOT NULL,day TEXT NOT NULL,kind TEXT NOT NULL,PRIMARY KEY(user_id,day,kind),
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS partners(
 id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,name TEXT NOT NULL,sign TEXT NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS tickets(
 id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,status TEXT NOT NULL DEFAULT 'open',
 category TEXT NOT NULL DEFAULT 'general',created REAL NOT NULL,updated REAL NOT NULL,
 assigned_to INTEGER,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE UNIQUE INDEX IF NOT EXISTS one_open_ticket ON tickets(user_id) WHERE status='open';
CREATE TABLE IF NOT EXISTS ticket_messages(
 id INTEGER PRIMARY KEY AUTOINCREMENT,ticket_id INTEGER NOT NULL,role TEXT NOT NULL,actor_id INTEGER,
 text TEXT NOT NULL,created REAL NOT NULL,FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS staff_routes(
 chat_id INTEGER NOT NULL,message_id INTEGER NOT NULL,ticket_id INTEGER NOT NULL,
 PRIMARY KEY(chat_id,message_id),FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS outbox(
 id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,kind TEXT NOT NULL,chat_id INTEGER NOT NULL,
 payload TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,next_try REAL NOT NULL DEFAULT 0,
 created REAL NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS outbox_due ON outbox(next_try,id);
CREATE TABLE IF NOT EXISTS log_messages(
 user_id INTEGER NOT NULL,chat_id INTEGER NOT NULL,message_id INTEGER NOT NULL,created REAL NOT NULL,
 PRIMARY KEY(chat_id,message_id),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS goal_progress(
 channel_id INTEGER NOT NULL,epoch TEXT NOT NULL,count INTEGER NOT NULL DEFAULT 0,complete INTEGER NOT NULL DEFAULT 0,
 checked REAL NOT NULL DEFAULT 0,PRIMARY KEY(channel_id,epoch));
CREATE TABLE IF NOT EXISTS join_markers(
 channel_id INTEGER NOT NULL,epoch TEXT NOT NULL,user_id INTEGER NOT NULL,verified INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(channel_id,epoch,user_id),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS anti_abuse(
 scope TEXT NOT NULL,token TEXT NOT NULL,created REAL NOT NULL,PRIMARY KEY(scope,token));
CREATE TABLE IF NOT EXISTS campaigns(
 code TEXT PRIMARY KEY,title TEXT NOT NULL,created REAL NOT NULL);
"""


async def upgrade(conn):
    async with conn.execute("PRAGMA table_info(users)") as cur:
        columns = {row[1] for row in await cur.fetchall()}
    for name, declaration in COLUMNS.items():
        if name not in columns:
            await conn.execute(f"ALTER TABLE users ADD COLUMN {name} {declaration}")
            if name == "language_selected":
                # Existing installations already have saved language preferences.
                placeholders = ",".join("?" for _ in LANGS)
                await conn.execute(f"UPDATE users SET language_selected=1 WHERE lang IN ({placeholders})", tuple(LANGS))
    await conn.executescript(SCHEMA)
    async with conn.execute("SELECT 1 FROM settings WHERE key='analytics_since'") as cur:
        seeded = await cur.fetchone()
    if not seeded:
        # Historical registrations are known. Historical reading activity is not invented.
        async with conn.execute("SELECT created FROM users") as cur:
            while rows := await cur.fetchmany(1000):
                for row in rows:
                    day = datetime.fromtimestamp(row[0], ZoneInfo("Asia/Tehran")).date().isoformat()
                    await conn.execute(
                        "INSERT INTO metric_days VALUES(?,'register','',1) ON CONFLICT(day,kind,detail) DO UPDATE SET count=count+1",
                        (day,),
                    )
        await conn.execute("INSERT INTO settings VALUES(?,?)", ("analytics_since", json.dumps(time.time())))
    await conn.execute(
        "INSERT OR IGNORE INTO settings VALUES(?,?)", ("anti_abuse_seed", json.dumps(secrets.token_hex(32)))
    )
    await conn.execute("PRAGMA user_version=2")
