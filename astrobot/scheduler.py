from __future__ import annotations

import asyncio
import html
import logging
import time
from zoneinfo import ZoneInfo

from .core import SIGNS, next_delivery, now_utc, sign_label
from .services import CREDIT, TelegramError, Unavailable
from .i18n import t

log = logging.getLogger(__name__)


async def channel_cards(app, job):
    lang, mode = job["lang"], job["kind"]
    if mode == "tarot":
        result = await app.horo.tarot(lang, "channel:" + str(job["chat_id"]))
    elif mode == "general":
        # A transparent digest of the actual 12 source readings, not an invented
        # universal forecast. Keep each excerpt intact and split between signs.
        result = []
        title = {
            "zh": "十二星座每日运势摘要",
            "hi": "बारह राशियों का दैनिक सार",
            "ru": "Ежедневный обзор 12 знаков",
            "he": "סיכום יומי ל־12 המזלות",
            "es": "Resumen diario de los 12 signos",
            "fr": "Résumé quotidien des 12 signes",
            "fa": "گزیده فال روزانه ۱۲ برج",
            "en": "Daily digest: 12 zodiac signs",
            "ar": "مقتطفات الأبراج اليومية",
            "tr": "12 burç için günlük özet",
        }[lang]
        buffer = "<b>" + html.escape(title) + "</b>\n\n"
        for sign in SIGNS:
            data = await app.horo.reading(sign, "daily")
            text, translated = await app.horo.translate(data["horoscope"], lang)
            excerpt = text[:140].rsplit(" ", 1)[0] + "…" if len(text) > 140 else text
            label = sign_label(sign, lang)
            if not translated:
                label += " (EN)"
            part = (
                "<b>"
                + html.escape(label)
                + "</b> · "
                + html.escape(data["date"])
                + "\n"
                + html.escape(excerpt)
                + "\n\n"
            )
            if len(buffer) + len(part) > 3000:
                result.append(buffer + CREDIT)
                buffer = ""
            buffer += part
        if buffer:
            result.append(buffer + CREDIT)
    else:
        result = []
        signs = SIGNS if job["sign"] == "all" else (job["sign"],)
        for sign in signs:
            if mode == "yearly":
                exists = await app.db.one(
                    "SELECT 1 FROM annual WHERE year=? AND sign=? AND lang=?", (now_utc().year, sign, lang)
                )
                if not exists:
                    continue
            result.extend(await app.horo.cards(sign, mode, lang))
        if not result:
            raise Unavailable("No annual editor content")
    footer = await app.db.setting("footer", "")
    if footer:
        result = [card + "\n\n" + html.escape(footer) for card in result]
    return result


class Scheduler:
    def __init__(self, app):
        self.app = app
        self.tasks = []

    def start(self):
        self.tasks = [
            asyncio.create_task(self.loop(fn, delay), name=fn.__name__)
            for fn, delay in [
                (self.personal, 15),
                (self.channels, 20),
                (self.broadcasts, 5),
                (self.cleanup, 3600),
                (self.outbox, 3),
            ]
        ]

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def loop(self, fn, delay):
        while True:
            try:
                await fn()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # Avoid logging user data, birth dates, tokens or request URLs.
                log.error("Worker %s failed (%s)", fn.__name__, type(exc).__name__)
            await asyncio.sleep(delay)

    async def personal(self):
        app = self.app
        rows = await app.db.all(
            "SELECT id FROM users WHERE subscribed=1 AND blocked=0 AND banned=0 AND sign IS NOT NULL AND next_due<=? ORDER BY next_due LIMIT 100",
            (time.time(),),
        )
        for row in rows:
            uid = row["id"]
            async with app.lock(uid):
                user = await app.db.user(uid)
                if (
                    not user
                    or not user["subscribed"]
                    or user["blocked"]
                    or user["next_due"] > time.time()
                    or user["banned"]
                    or not user["sign"]
                ):
                    continue
                day = now_utc().astimezone(ZoneInfo(user["zone"])).date().isoformat()
                scope = f"user:{uid}"
                try:
                    allowed = await app.membership.allowed(uid)
                    if allowed and not await app.db.sent(scope, day, 0):
                        payload_key = f"personal-payload:{uid}:{day}"
                        payload = await app.db.cached(payload_key)
                        if payload is None:
                            cards = await app.horo.cards(user["sign"], "daily", user["lang"])
                            if is_birthday(user):
                                cards.insert(
                                    0,
                                    html.escape(
                                        t(user["lang"], "birthday_text").format(
                                            name=user.get("nickname") or user["name"]
                                        )
                                    ),
                                )
                            hid = await app.extra.save_history(uid, "daily", user["sign"], user["lang"], cards)
                            payload = {"cards": cards, "history_id": hid}
                            await app.db.cache(payload_key, payload, 86400 * 2)
                        if isinstance(payload, list):  # Upgrade from v1 in-flight payloads.
                            payload = {
                                "cards": payload,
                                "history_id": await app.extra.save_history(
                                    uid, "daily", user["sign"], user["lang"], payload
                                ),
                            }
                            await app.db.cache(payload_key, payload, 86400 * 2)
                        cards = payload["cards"]
                        for part, card in enumerate(cards, 1):
                            if not await app.db.sent(scope, day, part):
                                await app.send(uid, card)
                                await app.db.mark(scope, day, part)
                        await app.db.mark(scope, day, 0)
                        await app.extra.completed(
                            uid, "daily", user["sign"], source="scheduled", history_id=payload["history_id"]
                        )
                        await app.db.execute("DELETE FROM cache WHERE key=?", (payload_key,))
                    await app.db.execute(
                        "UPDATE users SET next_due=? WHERE id=?", (next_delivery(user["clock"], user["zone"]), uid)
                    )
                except TelegramError as exc:
                    if exc.code == 403:
                        await app.db.execute("UPDATE users SET blocked=1,subscribed=0 WHERE id=?", (uid,))
                    else:
                        await app.db.execute("UPDATE users SET next_due=? WHERE id=?", (time.time() + 300, uid))
                except Unavailable:
                    await app.db.execute("UPDATE users SET next_due=? WHERE id=?", (time.time() + 300, uid))

    async def channels(self):
        app = self.app
        rows = await app.db.all(
            "SELECT id FROM jobs WHERE enabled=1 AND next_due<=? AND retry_at<=? ORDER BY next_due LIMIT 20",
            (time.time(), time.time()),
        )
        for row in rows:
            async with app.job_lock:
                job = await app.db.one("SELECT * FROM jobs WHERE id=?", (row["id"],))
                if not job or not job["enabled"] or job["next_due"] > time.time():
                    continue
                scope = "job:" + str(job["id"])
                slot = str(job["next_due"])
                payload_key = f"jobpayload:{job['id']}:{slot}"
                try:
                    cards = await app.db.cached(payload_key)
                    if cards is None:
                        cards = await channel_cards(app, job)
                        await app.db.cache(payload_key, cards, 86400 * 45)
                    for part, card in enumerate(cards):
                        if not await app.db.sent(scope, slot, part):
                            await app.tg.send(job["chat_id"], card)
                            await app.db.mark(scope, slot, part)
                    # Skip missed intervals: downtime never causes a burst of old posts.
                    interval = job["hours"] * 3600
                    due = job["next_due"] + (int((time.time() - job["next_due"]) // interval) + 1) * interval
                    await app.db.execute(
                        "UPDATE jobs SET next_due=?,retry_at=0,last_error=? WHERE id=?", (due, "", job["id"])
                    )
                    await app.db.execute("DELETE FROM cache WHERE key=?", (payload_key,))
                    await app.extra.analytics.record(None, "channel", job["kind"], source="scheduled", audit=False)
                except (TelegramError, Unavailable) as exc:
                    reason = (
                        f"Telegram {exc.code}" if isinstance(exc, TelegramError) else "Provider/transport unavailable"
                    )
                    disabled = isinstance(exc, TelegramError) and exc.code in (400, 403)
                    await app.db.execute(
                        "UPDATE jobs SET retry_at=?,last_error=?,enabled=? WHERE id=?",
                        (time.time() + 300, reason, int(not disabled), job["id"]),
                    )
                    log.warning("Channel job %s delayed: %s", job["id"], reason)

    async def broadcasts(self):
        app = self.app
        batch = await app.db.one("SELECT * FROM broadcasts WHERE enabled=1 ORDER BY id LIMIT 1")
        if not batch:
            return
        users = await app.db.all(
            "SELECT id FROM users WHERE id>? AND id<=? AND blocked=0 AND banned=0 ORDER BY id LIMIT 50",
            (batch["cursor"], batch["max_user_id"]),
        )
        if not users:
            await app.db.execute("UPDATE broadcasts SET enabled=0 WHERE id=?", (batch["id"],))
            return
        for row in users:
            current = await app.db.one("SELECT enabled FROM broadcasts WHERE id=?", (batch["id"],))
            if not current or not current["enabled"]:
                break
            uid = row["id"]
            async with app.lock(uid):
                user = await app.db.user(uid)
                if not user:
                    await app.db.execute("UPDATE broadcasts SET cursor=? WHERE id=?", (uid, batch["id"]))
                    continue
                try:
                    if await app.membership.allowed(uid):
                        scope = f"broadcast:{batch['id']}"
                        if not await app.db.sent(scope, str(uid)):
                            await app.send(uid, html.escape(batch["text"]))
                            await app.db.mark(scope, str(uid))
                            await app.db.execute("UPDATE broadcasts SET sent=sent+1 WHERE id=?", (batch["id"],))
                except TelegramError as exc:
                    if exc.code == 403:
                        await app.db.execute("UPDATE users SET blocked=1,subscribed=0 WHERE id=?", (uid,))
                    elif exc.code == 429 or exc.code >= 500:
                        return  # Retry the same recipient next cycle.
                    await app.db.execute("UPDATE broadcasts SET failed=failed+1 WHERE id=?", (batch["id"],))
                except Unavailable:
                    return
                await app.db.execute("UPDATE broadcasts SET cursor=? WHERE id=?", (uid, batch["id"]))

    async def outbox(self):
        await self.app.extra.support.drain()

    async def cleanup(self):
        await self.app.db.cleanup()


def is_birthday(user, now=None):
    import calendar
    from datetime import date
    import jdatetime

    if not user.get("birth"):
        return False
    today = (now or now_utc()).astimezone(ZoneInfo(user["zone"])).date()
    born = date.fromisoformat(user["birth"])
    if user.get("birth_calendar") == "j":
        birthday = jdatetime.date.fromgregorian(date=born)
        current = jdatetime.date.fromgregorian(date=today)
        target_day = birthday.day
        if birthday.month == 12 and birthday.day == 30 and not current.isleap():
            target_day = 29
        return (current.month, current.day) == (birthday.month, target_day)
    target_day = 28 if born.month == 2 and born.day == 29 and not calendar.isleap(today.year) else born.day
    return (today.month, today.day) == (born.month, target_day)
