from __future__ import annotations

import asyncio
import html
import json
import time

from .analytics import profile_text
from .core import DIGITS, split_text
from .i18n import t
from .services import TelegramError, Unavailable


class Support:
    def __init__(self, app, analytics):
        self.app, self.analytics = app, analytics
        self.privacy_lock = asyncio.Lock()
        self.ticket_lock = asyncio.Lock()

    async def submit(self, uid, text, context=None):
        app = self.app
        context = context or {}
        user = await app.db.user(uid)
        if not user:
            return
        lang = user["lang"]
        if not text.strip() and not context.get("media"):
            await app.send(uid, html.escape(t(lang, "support_prompt")), await app.back(lang))
            return
        if len(text) > 1800:
            await app.send(uid, html.escape(t(lang, "invalid")))
            return
        recent = await app.db.one(
            "SELECT COUNT(*) n FROM ticket_messages m JOIN tickets t ON t.id=m.ticket_id WHERE t.user_id=? AND m.role='user' AND m.created>?",
            (uid, time.time() - 3600),
        )
        if recent["n"] >= 10:
            await app.send(uid, html.escape(t(lang, "limited")))
            return
        async with self.ticket_lock:
            ticket = await app.db.one("SELECT * FROM tickets WHERE user_id=? AND status='open'", (uid,))
            if ticket:
                tid = ticket["id"]
                await app.db.execute("UPDATE tickets SET updated=? WHERE id=?", (time.time(), tid))
            else:
                tid = await app.db.execute(
                    "INSERT INTO tickets(user_id,created,updated) VALUES(?,?,?)", (uid, time.time(), time.time())
                )
            await app.db.execute(
                "INSERT INTO ticket_messages(ticket_id,role,actor_id,text,created) VALUES(?,?,?,?,?)",
                (tid, "user", uid, text or "[attachment]", time.time()),
            )
            group = await app.db.setting("support_group")
            destinations = [group] if group else sorted(app.cfg.admins)
            header = f"<b>💌 تیکت #{tid}</b>\n" + await profile_text(app.db, uid)
            header += (
                "\n\nبرای پاسخ روی همین پیام Reply کنید.\n"
                + f"<code>/reply {tid} متن پاسخ</code> · <code>/close {tid}</code>"
            )
            blocks = [header] + [html.escape(chunk) for chunk in split_text(text, 450)]
            for chat in destinations:
                for block in blocks:
                    await self.enqueue(uid, "ticket", chat, {"text": block, "ticket_id": tid})
                if context.get("media") and context.get("message_id"):
                    await self.enqueue(
                        uid,
                        "ticket",
                        chat,
                        {"ticket_id": tid, "from_chat_id": uid, "source_message": context["message_id"]},
                    )
            await self.analytics.record(uid, "support", source="private")
            await app.db.set_state(uid)
            await app.send(
                uid,
                html.escape(t(lang, "support_sent").format(id=tid)),
                [[await app.button(lang, "support", "support"), await app.button(lang, "tickets", "tickets")]]
                + await app.back(lang),
            )

    async def enqueue(self, uid, kind, chat, payload):
        await self.app.db.execute(
            "INSERT INTO outbox(user_id,kind,chat_id,payload,created) VALUES(?,?,?,?,?)",
            (uid, kind, chat, json.dumps(payload, ensure_ascii=False), time.time()),
        )

    async def show_ticket(self, admin, tid):
        app = self.app
        if admin not in app.cfg.admins:
            return
        ticket = await app.db.one("SELECT * FROM tickets WHERE id=?", (tid,))
        if not ticket:
            await app.send(admin, "تیکت وجود ندارد.")
            return
        profile = await profile_text(app.db, ticket["user_id"])
        await app.send(
            admin,
            f"<b>تیکت #{tid} · {ticket['status']}</b>\n" + profile,
            [
                [
                    await app.button("fa", "", f"admin:treply:{tid}", text="💌 پاسخ"),
                    await app.button("fa", "", f"admin:tclose:{tid}", text="بستن تیکت"),
                ],
                [await app.button("fa", "", f"admin:user:{ticket['user_id']}", text="پرونده کاربر")],
            ],
        )
        messages = await app.db.all("SELECT * FROM ticket_messages WHERE ticket_id=? ORDER BY id DESC LIMIT 8", (tid,))
        for m in reversed(messages):
            for chunk in split_text(m["text"], 500):
                await app.send(admin, html.escape(f"{m['role']}: {chunk}"))

    async def reply(self, admin, tid, text, context=None):
        app = self.app
        if admin not in app.cfg.admins:
            return False
        context = context or {}
        if not text.strip() and not context.get("media"):
            return False
        if len(text) > 1800:
            await app.send(admin, "پاسخ حداکثر ۱۸۰۰ حرف باشد.")
            return False
        async with self.privacy_lock:
            ticket = await app.db.one("SELECT * FROM tickets WHERE id=?", (tid,))
            if not ticket:
                await app.send(admin, "تیکت یا کاربر حذف شده است.")
                return False
            user = await app.db.user(ticket["user_id"])
            if not user or ticket["status"] != "open":
                await app.send(admin, "تیکت بسته است یا کاربر دیگر در ربات نیست.")
                return False
            try:
                await app.send(user["id"], html.escape(t(user["lang"], "support_reply").format(id=tid)))
                for chunk in split_text(text, 500):
                    await app.send(user["id"], html.escape(chunk))
                if context.get("media") and context.get("message_id"):
                    if hasattr(app.tg, "throttle"):
                        await app.tg.throttle(user["id"])
                    await app.tg.call(
                        "copyMessage",
                        chat_id=user["id"],
                        from_chat_id=context["chat_id"],
                        message_id=context["message_id"],
                    )
            except (TelegramError, Unavailable):
                await app.send(
                    admin,
                    "پاسخ تحویل نشد؛ دسترسی کاربر یا اتصال تلگرام را بررسی کن. متن پاسخ ارسال‌شده را پیش از تلاش دوباره بررسی کن.",
                )
                return False
            await app.db.execute(
                "INSERT INTO ticket_messages(ticket_id,role,actor_id,text,created) VALUES(?,?,?,?,?)",
                (tid, "staff", admin, text or "[attachment]", time.time()),
            )
            await app.db.execute("UPDATE tickets SET updated=?,assigned_to=? WHERE id=?", (time.time(), admin, tid))
            await self.analytics.record(user["id"], "reply", source="staff")
        await app.send(admin, f"پاسخ تیکت #{tid} ارسال شد ✅")
        return True

    async def close(self, actor, tid):
        app = self.app
        async with self.privacy_lock:
            ticket = await app.db.one("SELECT * FROM tickets WHERE id=?", (tid,))
            if not ticket or (actor not in app.cfg.admins and ticket["user_id"] != actor):
                return False
            await app.db.execute("UPDATE tickets SET status='closed',updated=? WHERE id=?", (time.time(), tid))
            user = await app.db.user(ticket["user_id"])
            if user:
                await app.send(actor, html.escape(t(user["lang"], "ticket_closed")))
        return True

    async def staff_message(self, admin, chat, text, reply_to=None, context=None):
        app = self.app
        if admin not in app.cfg.admins:
            return False
        if text.strip().split("@")[0] == "/chatid":
            await app.send(chat, f"<code>{chat}</code>")
            return True
        group = await app.db.setting("support_group")
        if chat not in (admin, group):
            return False
        context = {**(context or {}), "chat_id": chat}
        command = text.strip().split(maxsplit=2)
        if command and command[0].split("@")[0] in ("/reply", "/ticket", "/close"):
            try:
                tid = int(command[1].translate(DIGITS))
            except (IndexError, ValueError):
                await app.send(chat, "/reply ID متن\n/ticket ID\n/close ID")
                return True
            name = command[0].split("@")[0]
            if name == "/reply":
                await self.reply(admin, tid, command[2] if len(command) > 2 else "", context)
            elif name == "/ticket":
                await self.show_ticket(admin, tid)
            else:
                await self.close(admin, tid)
            return True
        if reply_to:
            route = await app.db.one(
                "SELECT ticket_id FROM staff_routes WHERE chat_id=? AND message_id=?", (chat, reply_to)
            )
            if route:
                if text.startswith("!note "):
                    await app.db.execute(
                        "INSERT INTO ticket_messages(ticket_id,role,actor_id,text,created) VALUES(?,?,?,?,?)",
                        (route["ticket_id"], "internal", admin, text[6:1806], time.time()),
                    )
                    await app.send(chat, "یادداشت داخلی ذخیره شد؛ برای کاربر ارسال نشد ✅")
                else:
                    await self.reply(admin, route["ticket_id"], text, context)
                return True
        return False

    async def drain(self):
        app = self.app
        rows = await app.db.all(
            "SELECT * FROM outbox WHERE next_try<=? AND attempts<10 ORDER BY CASE kind WHEN 'delete' THEN 0 WHEN 'ticket' THEN 1 ELSE 2 END,id LIMIT 20",
            (time.time(),),
        )
        for row in rows:
            async with self.privacy_lock:
                # It may have been removed by a profile deletion while waiting.
                if not await app.db.one("SELECT id FROM outbox WHERE id=?", (row["id"],)):
                    continue
                payload = json.loads(row["payload"])
                try:
                    if row["kind"] == "delete":
                        await app.tg.call("deleteMessage", chat_id=row["chat_id"], message_id=payload["message_id"])
                        await app.db.execute("DELETE FROM outbox WHERE id=?", (row["id"],))
                        continue
                    if payload.get("source_message"):
                        if hasattr(app.tg, "throttle"):
                            await app.tg.throttle(row["chat_id"])
                        result = await app.tg.call(
                            "copyMessage",
                            chat_id=row["chat_id"],
                            from_chat_id=payload["from_chat_id"],
                            message_id=payload["source_message"],
                        )
                    else:
                        result = await app.send(row["chat_id"], payload["text"])
                    mid = (result or {}).get("message_id")
                    if mid and row["user_id"]:
                        await app.db.execute(
                            "INSERT OR IGNORE INTO log_messages VALUES(?,?,?,?)",
                            (row["user_id"], row["chat_id"], mid, time.time()),
                        )
                    if mid and payload.get("ticket_id"):
                        await app.db.execute(
                            "INSERT OR REPLACE INTO staff_routes VALUES(?,?,?)",
                            (row["chat_id"], mid, payload["ticket_id"]),
                        )
                    await app.db.execute("DELETE FROM outbox WHERE id=?", (row["id"],))
                except (TelegramError, Unavailable) as exc:
                    if row["kind"] == "delete" and isinstance(exc, TelegramError) and exc.code == 400:
                        # Telegram may refuse old/already-deleted messages; do not loop forever.
                        await app.db.execute("DELETE FROM outbox WHERE id=?", (row["id"],))
                    else:
                        await app.db.execute(
                            "UPDATE outbox SET attempts=attempts+1,next_try=? WHERE id=?",
                            (time.time() + min(3600, 30 * 2 ** row["attempts"]), row["id"]),
                        )
