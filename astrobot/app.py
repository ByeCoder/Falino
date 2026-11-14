from __future__ import annotations

import asyncio
from contextlib import suppress
import html
import math
import re
import time
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

from .core import (
    DIGITS,
    LANGS,
    PERIODS,
    SIGNS,
    next_delivery,
    now_utc,
    parse_birth,
    sign_for,
    sign_label,
    validate_clock,
)
from .i18n import TEXTS, t
from .services import CREDIT, TelegramError, Unavailable
from .experience import Experience
from .metadata import commands_for


class App:
    def __init__(self, config, db, tg, horo, membership):
        self.cfg, self.db, self.tg, self.horo, self.membership = config, db, tg, horo, membership
        self.username = ""
        self.bot_id = 0
        self.user_locks = [asyncio.Lock() for _ in range(256)]
        self.clicks = {}  # Pruned in dispatch; only short-term anti-spam timestamps.
        self.job_lock = asyncio.Lock()
        self.extra = Experience(self)

    def lock(self, uid):
        return self.user_locks[uid % len(self.user_locks)]

    async def button(self, lang, key, callback=None, *, text=None, url=None):
        theme = await self.db.setting("theme", {})
        labels = await self.db.setting("labels", {})
        label = text or labels.get(lang + ":" + key) or t(lang, key)
        b = {"text": label[:64]}
        b["url" if url else "callback_data"] = url or callback or key
        if theme.get("style") in ("primary", "success", "danger"):
            b["style"] = theme["style"]
        if theme.get("emoji"):
            b["icon_custom_emoji_id"] = str(theme["emoji"])
        return b

    async def send(self, uid, text, rows=None):
        return await self.tg.send(uid, text, rows)

    async def back(self, lang):
        return [[await self.button(lang, "back", "home")]]

    async def menu(self, uid, lang):
        welcome = await self.db.setting("welcome:" + lang, t(lang, "welcome"))
        theme = await self.db.setting("theme", {})
        if theme.get("text_emoji"):
            welcome = f'<tg-emoji emoji-id="{theme["text_emoji"]}">✨</tg-emoji> ' + html.escape(welcome)
        else:
            welcome = html.escape(welcome)
        user = await self.db.user(uid)
        if user and (user.get("nickname") or user["name"]):
            welcome = html.escape(user.get("nickname") or user["name"]) + " 💛\n" + welcome
        keys = [
            ("daily", "p:daily"),
            ("tarot", "tarot"),
            ("weekly", "p:weekly"),
            ("monthly", "p:monthly"),
            ("spread", "spread"),
            ("compat", "compat"),
            ("profile", "profile"),
            ("birth", "birth"),
            ("rewards", "rewards"),
            ("history", "history"),
            ("explore", "explore"),
            ("support", "support"),
            ("subscribe", "subscribe"),
            ("schedule", "schedule"),
            ("language", "language"),
            ("ref", "ref"),
        ]
        buttons = [await self.button(lang, key, data) for key, data in keys]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        if uid in self.cfg.admins:
            rows.append([await self.button(lang, "panel", "admin:home", text="⚙️ پنل مدیریت")])
        await self.send(uid, welcome, rows)

    async def choose(self, uid, lang, prefix):
        buttons = [await self.button(lang, s, f"{prefix}:{s}", text=sign_label(s, lang)) for s in SIGNS]
        await self.send(
            uid, html.escape(t(lang, "choose")), [buttons[i : i + 3] for i in range(0, 12, 3)] + await self.back(lang)
        )

    async def gate(self, uid, lang):
        if await self.membership.allowed(uid):
            return True
        rows = [
            [await self.button(lang, "join", url=c["url"], text=c["title"])]
            for c in await self.membership.active_channels()
        ]
        rows.append([await self.button(lang, "check", "check")])
        await self.send(uid, html.escape(t(lang, "join")), rows)
        return False

    async def choose_language(self, uid):
        rows = [[await self.button("en", code, "lang:" + code, text=label)] for code, label in LANGS.items()]
        await self.send(uid, "🌐 Choose your language · زبان خودت را انتخاب کن", rows)

    async def dispatch(self, uid, name, language, text="", callback=None, identity=None, context=None):
        async with self.lock(uid):
            now = time.monotonic()
            if callback and now - self.clicks.get(uid, 0) < 0.7:
                return
            self.clicks[uid] = now
            if len(self.clicks) > 4096:
                self.clicks = {k: v for k, v in self.clicks.items() if now - v < 60}
            old = await self.db.user(uid)
            # A stale button after account deletion must not recreate a profile.
            if old is None and callback:
                return
            if old is None and not text.startswith("/start"):
                await self.send(uid, "/start")
                return
            parts = text.strip().split(maxsplit=1)
            command = parts[0].split("@")[0].lower() if parts else ""
            referral, source = None, None
            if old is None and command == "/start" and len(parts) == 2:
                arg = parts[1]
                if arg.startswith("ref_") and arg[4:].isdigit():
                    candidate = int(arg[4:])
                    if candidate != uid and await self.db.user(candidate):
                        referral = candidate
                elif arg.startswith("src_"):
                    source = arg[4:68]
            if old is None and identity is None:
                identity = {"telegram_lang": language or ""}
            await self.db.touch(uid, name, "", referral, source, identity)
            await self.extra.visit(uid, new=old is None)
            user = await self.db.user(uid)
            lang = user["lang"]
            pending_language = not user["language_selected"] or lang not in LANGS
            choosing = bool(callback and callback.startswith("lang:"))
            privacy_exit = command in ("/delete_me", "/stop", "/privacy") or callback in (
                "delete",
                "delete:yes",
                "privacy",
            )
            if pending_language and not choosing and not privacy_exit:
                await self.db.set_state(uid)
                return await self.choose_language(uid)
            if command in ("/cancel", "/start", "/menu") or callback == "home":
                await self.db.set_state(uid)
            if command == "/cancel":
                return await self.menu(uid, lang)
            if command == "/stop":
                await self.db.execute("UPDATE users SET subscribed=0 WHERE id=?", (uid,))
                return await self.send(uid, html.escape(t(lang, "off")))
            if command == "/delete_me" or callback == "delete":
                return await self.send(
                    uid,
                    html.escape(t(lang, "confirm_delete")),
                    [[await self.button(lang, "confirm", "delete:yes")]] + await self.back(lang),
                )
            if callback == "delete:yes":
                async with self.extra.support.privacy_lock:
                    await self.db.forget(uid)
                return await self.send(uid, html.escape(t(lang, "deleted")))
            if command == "/language" or callback == "language":
                return await self.choose_language(uid)
            if callback and callback.startswith("lang:"):
                chosen = callback.split(":")[1]
                if chosen not in LANGS:
                    return
                await self.db.execute("UPDATE users SET lang=?,language_selected=1 WHERE id=?", (chosen, uid))
                await self.db.set_state(uid)
                with suppress(TelegramError, Unavailable):
                    await self.tg.call(
                        "setMyCommands", commands=commands_for(chosen), scope={"type": "chat", "chat_id": uid}
                    )
                if pending_language:
                    await self.send(uid, t(chosen, "welcome_privacy"))
                if await self.gate(uid, chosen):
                    return await self.menu(uid, chosen)
                return
            if await self.extra.public_route(uid, user, text, callback, context):
                return
            reply_state = await self.db.state(uid)
            if (
                uid in self.cfg.admins
                and reply_state
                and reply_state["kind"] == "admin:reply"
                and not callback
                and not text.startswith("/")
            ):
                if await self.extra.support.reply(uid, reply_state["ticket"], text, context):
                    await self.db.set_state(uid)
                return
            if user["banned"] and uid not in self.cfg.admins:
                return await self.send(uid, html.escape(t(lang, "limited")))
            if command == "/user" and uid in self.cfg.admins:
                await self.db.set_state(uid, {"kind": "admin:users"})
                return await self.extra.admin_input(uid, parts[1] if len(parts) > 1 else "", "admin:users")
            if not await self.gate(uid, lang):
                return
            if command in ("/panel", "/admin", "/stats") or (callback and callback.startswith("admin:")):
                if uid not in self.cfg.admins:
                    return
                await self.db.set_state(uid)
                return await self.admin(uid, callback or ("admin:stats" if command == "/stats" else "admin:home"))
            if command in ("/start", "/menu") or callback in ("home", "check"):
                if old is None:
                    await self.send(uid, html.escape(t(lang, "welcome_privacy")))
                return await self.menu(uid, lang)
            if await self.extra.route(uid, user, text, callback):
                return
            if command == "/help":
                return await self.send(uid, html.escape(t(lang, "help")), await self.back(lang))
            if command == "/about":
                return await self.send(uid, html.escape(t(lang, "about")) + "\n\n" + CREDIT, await self.back(lang))
            if callback and callback.startswith("cal:"):
                cal = callback.split(":")[1]
                if cal not in ("j", "g"):
                    return
                await self.db.set_state(uid, {"kind": "birth", "calendar": cal})
                return await self.send(uid, html.escape(t(lang, "birth_prompt")), await self.back(lang))
            if command == "/birthdate" or callback == "birth":
                await self.db.set_state(uid)
                return await self.send(
                    uid,
                    html.escape(t(lang, "calendar")),
                    [
                        [
                            await self.button(lang, key, data)
                            for key, data in (
                                [("jalali", "cal:j"), ("gregorian", "cal:g")]
                                if lang == "fa"
                                else [("gregorian", "cal:g"), ("jalali", "cal:j")]
                            )
                        ]
                    ],
                )
            if command in ("/change_zodiac", "/horoscope"):
                return await self.choose(uid, lang, "set")
            if callback and callback.startswith("set:"):
                sign = callback.split(":")[1]
                if sign in SIGNS:
                    await self.db.execute("UPDATE users SET sign=?,birth=NULL WHERE id=?", (sign, uid))
                    return await self.show(uid, sign, "daily", lang)
                return
            if command == "/profile" or callback == "profile":
                value = f"<b>{html.escape(user['name'])}</b>\n"
                value += html.escape(str(user["birth"] or "—")) + "\n"
                value += html.escape(sign_label(user["sign"], lang) if user["sign"] else "—") + "\n"
                value += html.escape(f"{user['clock']} {user['zone']}") + "\n"
                value += html.escape(t(lang, "on" if user["subscribed"] else "off"))
                value += f"\n✨ {user['points']} " + html.escape(t(lang, "points")) + f" | 🔥 {user['streak']}"
                return await self.send(
                    uid,
                    value,
                    [
                        [await self.button(lang, "birth", "birth"), await self.button(lang, "delete", "delete")],
                        [
                            await self.button(
                                lang, "", "name", text="✏️ " + html.unescape(user.get("nickname") or user["name"])
                            )
                        ],
                    ]
                    + await self.back(lang),
                )
            if command in ("/daily", "/subscribe") or callback == "subscribe":
                if not user["sign"]:
                    return await self.send(uid, html.escape(t(lang, "need_birth")), await self.back(lang))
                enabled = not user["subscribed"]
                due = next_delivery(user["clock"], user["zone"])
                await self.db.execute("UPDATE users SET subscribed=?,next_due=? WHERE id=?", (int(enabled), due, uid))
                return await self.send(uid, html.escape(t(lang, "on" if enabled else "off")), await self.back(lang))
            if command == "/schedule" or callback == "schedule":
                await self.db.set_state(uid, {"kind": "schedule"})
                return await self.send(uid, html.escape(t(lang, "clock_prompt")), await self.back(lang))
            period = {
                "/today": "daily",
                "/update": "daily",
                "/weekly": "weekly",
                "/monthly": "monthly",
                "/yearly": "yearly",
            }.get(command)
            if callback and callback.startswith("p:"):
                period = callback.split(":")[1]
            if period in PERIODS:
                if not user["sign"]:
                    return await self.choose(uid, lang, "read:" + period)
                return await self.show(uid, user["sign"], period, lang)
            if callback and callback.startswith("read:"):
                _, period, sign = callback.split(":")
                if sign in SIGNS and period in PERIODS:
                    return await self.show(uid, sign, period, lang)
                return
            if command == "/tarot" or callback == "tarot":
                cards = await self.horo.tarot(lang, uid)
                hid = await self.extra.save_history(uid, "tarot", "", lang, cards)
                for card in cards:
                    await self.send(uid, card)
                await self.extra.completed(uid, "tarot", history_id=hid)
                return await self.send(
                    uid,
                    html.escape(t(lang, "feedback")),
                    await self.extra.reading_buttons(uid, hid, lang) + await self.back(lang),
                )
            if command == "/natal" or callback == "natal":
                if not user["birth"]:
                    return await self.send(uid, html.escape(t(lang, "need_birth")), await self.back(lang))
                await self.db.set_state(uid, {"kind": "natal"})
                return await self.send(uid, html.escape(t(lang, "natal_prompt")), await self.back(lang))
            if command == "/mood" or callback == "mood":
                await self.db.set_state(uid, {"kind": "mood"})
                return await self.send(uid, html.escape(t(lang, "mood_prompt")), await self.back(lang))
            if command == "/moods":
                rows = await self.db.all(
                    "SELECT day,score FROM moods WHERE user_id=? ORDER BY day DESC LIMIT 7", (uid,)
                )
                return await self.send(
                    uid, "\n".join(f"{r['day']}: {r['score']}/10" for r in rows) or "—", await self.back(lang)
                )
            if command == "/ref" or callback == "ref":
                row = await self.db.one("SELECT COUNT(*) AS n FROM users WHERE referred_by=?", (uid,))
                return await self.send(
                    uid,
                    f"https://t.me/{self.username}?start=ref_{uid}\n👥 {row['n']}\n✨ +30 / "
                    + html.escape(t(lang, "ref"))
                    + "\n"
                    + html.escape(t(lang, "referral_note")),
                    await self.back(lang),
                )
            if command == "/moon" or callback == "moon":
                epoch = datetime(2000, 1, 6, 18, 14, tzinfo=ZoneInfo("UTC"))
                age = ((now_utc() - epoch).total_seconds() / 86400) % 29.530588853
                phase = age / 29.530588853
                lit = (1 - math.cos(2 * math.pi * phase)) / 2 * 100
                key = (
                    "new"
                    if age < 1 or age > 28.53
                    else "full"
                    if abs(age - 14.765) < 1
                    else "waxing"
                    if age < 14.765
                    else "waning"
                )
                await self.send(
                    uid,
                    f"🌙 {html.escape(t(lang, key))} · {lit:.0f}%\n\n{html.escape(t(lang, 'moon_note'))}",
                    await self.back(lang),
                )
                await self.extra.completed(uid, "moon", source="local_approximation")
                return
            if command == "/compat" or callback == "compat":
                return await self.choose(uid, lang, "compat1")
            if callback and callback.startswith("compat1:"):
                first = callback.split(":")[1]
                if first in SIGNS:
                    return await self.choose(uid, lang, "compat2:" + first)
                return
            if callback and callback.startswith("compat2:"):
                _, a, b = callback.split(":")
                if a not in SIGNS or b not in SIGNS:
                    return
                # Explicit traditional element rubric, not a manufactured precision score.
                e1, e2 = SIGNS.index(a) % 4, SIGNS.index(b) % 4
                stars = "⭐⭐⭐" if e1 == e2 else "⭐⭐" if (e1 - e2) % 4 == 2 else "⭐"
                await self.send(
                    uid,
                    html.escape(f"{sign_label(a, lang)} + {sign_label(b, lang)}\n{stars}\n\n{t(lang, 'compat_note')}"),
                    await self.back(lang),
                )
                await self.extra.completed(uid, "compat", a + "+" + b, source="traditional_elements")
                return
            state = await self.db.state(uid)
            if state and not callback and not command.startswith("/"):
                return await self.input(uid, user, text, state)
            await self.send(uid, html.escape(t(lang, "help")), await self.back(lang))

    async def show(self, uid, sign, period, lang):
        cards = await self.horo.cards(sign, period, lang)
        annual = period != "yearly" or bool(
            await self.db.one("SELECT 1 FROM annual WHERE year=? AND sign=? AND lang=?", (now_utc().year, sign, lang))
        )
        hid = await self.extra.save_history(uid, period, sign, lang, cards) if annual else None
        for index, card in enumerate(cards):
            rows = None
            if index == len(cards) - 1:
                rows = [
                    [await self.button(lang, "daily", f"read:daily:{sign}"), await self.button(lang, "back", "home")]
                ]
                share = f"https://t.me/{self.username}?start=ref_{uid}"
                rows.append([await self.button(lang, "ref", url="https://t.me/share/url?url=" + quote(share, safe=""))])
                if hid:
                    rows.extend(await self.extra.reading_buttons(uid, hid, lang))
            await self.send(uid, card, rows)
        if annual:
            await self.extra.completed(uid, period, sign, history_id=hid)
        # A manual daily view suppresses the scheduled duplicate for that local date.
        if period == "daily":
            user = await self.db.user(uid)
            if user and user["sign"] == sign:
                day = now_utc().astimezone(ZoneInfo(user["zone"])).date().isoformat()
                await self.db.mark(f"user:{uid}", day, 0)

    async def input(self, uid, user, text, state):
        lang, kind = user["lang"], state["kind"]
        try:
            if kind.startswith("admin:"):
                if uid not in self.cfg.admins:
                    await self.db.set_state(uid)
                    return
                return await self.admin_input(uid, text, kind)
            if kind == "birth":
                born = parse_birth(text, state["calendar"])
                sign = sign_for(born)
                await self.db.execute(
                    "UPDATE users SET birth=?,sign=?,birth_calendar=? WHERE id=?",
                    (born.isoformat(), sign, state["calendar"], uid),
                )
                await self.extra.analytics.record(uid, "profile", "birth")
                await self.db.set_state(uid)
                await self.send(uid, html.escape(t(lang, "saved")))
                return await self.show(uid, sign, "daily", lang)
            if kind == "natal":
                clock, zone = validate_clock(text)
                if not user["birth"]:
                    raise ValueError("Birth date required")
                card = await self.horo.natal(uid, user["birth"], clock, zone, lang)
                await self.db.set_state(uid)
                await self.send(uid, card, await self.back(lang))
                await self.extra.completed(uid, "natal", source="planetary_api")
                return
            if kind == "schedule":
                clock, zone = validate_clock(text)
                await self.db.execute(
                    "UPDATE users SET clock=?,zone=?,next_due=? WHERE id=?",
                    (clock, zone, next_delivery(clock, zone), uid),
                )
            elif kind == "mood":
                score = int(text.translate(DIGITS).strip())
                if not 1 <= score <= 10:
                    raise ValueError("1..10")
                day = now_utc().astimezone(ZoneInfo(user["zone"])).date().isoformat()
                await self.db.execute("INSERT OR REPLACE INTO moods VALUES(?,?,?)", (uid, day, score))
            else:
                return
        except (ValueError, KeyError, OverflowError):
            return await self.send(uid, html.escape(t(lang, "invalid")), await self.back(lang))
        await self.db.set_state(uid)
        await self.send(uid, html.escape(t(lang, "saved")), await self.back(lang))

    async def admin(self, uid, action):
        if uid not in self.cfg.admins:
            return
        if await self.extra.admin(uid, action):
            return
        if action == "admin:home":
            groups = [
                ("stats", "📊 آمار روزانه / هفتگی / ماهانه / کلی"),
                ("users", "👤 پرونده کاربران"),
                ("tickets", "💬 صندوق پشتیبانی"),
                ("loggroup", "📒 گروه لاگ"),
                ("supportgroup", "🛟 گروه پاسخ‌گویی"),
                ("campaigns", "📈 کمپین‌های جذب"),
                ("members", "🔐 عضویت اجباری"),
                ("jobs", "⏰ زمان‌بندی کانال"),
                ("theme", "🎨 ظاهر دکمه‌ها"),
                ("labels", "✏️ متن دکمه‌ها"),
                ("welcome", "📝 متن شروع"),
                ("footer", "📎 امضای کانال"),
                ("annual", "📅 فال سالانه"),
                ("broadcast", "📣 پیام همگانی"),
                ("health", "🩺 وضعیت"),
            ]
            rows = [[await self.button("fa", "", "admin:" + key, text=label)] for key, label in groups]
            return await self.send(uid, "<b>پنل مدیریت</b>\nتنظیمات ماندگار است. برای لغو ورودی /cancel.", rows)
        if action == "admin:health":
            jobs = await self.db.one("SELECT COUNT(*) n FROM jobs WHERE enabled=1")
            queue = await self.db.one("SELECT COUNT(*) n,SUM(attempts>0) retries FROM outbox")
            tickets = await self.db.one("SELECT COUNT(*) n FROM tickets WHERE status='open'")
            await self.send(
                uid, f"صندوق ارسال: {queue['n']} | در تلاش مجدد: {queue['retries'] or 0}\nتیکت باز: {tickets['n']}"
            )
            return await self.send(
                uid,
                f"✅ پردازش فعال\nزمان UTC: {now_utc().isoformat(timespec='seconds')}\nزمان‌بندی فعال: {jobs['n']}\nترجمه: {'فعال' if self.cfg.llm_key and self.cfg.llm_model and self.cfg.llm_url else 'تنظیم نشده'}",
            )
        if action == "admin:members":
            channels = await self.db.setting("required_channels", [])
            await self.membership.active_channels()
            lines = []
            for c in channels:
                progress = await self.db.one(
                    "SELECT * FROM goal_progress WHERE channel_id=? AND epoch=?",
                    (c["id"], str(c.get("epoch", "legacy"))),
                )
                goal = c.get("goal", 0)
                lines.append(
                    f"{c['id']} | {c['title']} | {c.get('goal_mode', 'members')} | {(progress or {}).get('count', 0)}/{goal or '∞'} | {'پایان هدف ✅' if (progress or {}).get('complete') else 'فعال'}"
                )
            content = "\n".join(lines) or "هنوز کانالی ثبت نشده."
            await self.send(uid, html.escape(content))
            await self.db.set_state(uid, {"kind": "admin:members"})
            return await self.send(
                uid,
                "هر کانال در یک خط؛ فهرست جدید جایگزین قبلی می‌شود. ربات باید ادمین باشد.\nبدون هدف: <code>@YourChannel | https://t.me/YourChannel</code>\nهدف تعداد کل اعضا: <code>@YourChannel | https://t.me/YourChannel | members | 5000</code>\nهدف جذب جدید تأییدشده: <code>@YourChannel | https://t.me/YourChannel | joins | 100</code>\nبا رسیدن به هدف، همان شرط خودکار برداشته می‌شود. عضوهای قبلی در جذب جدید حساب نمی‌شوند. برای حذف همه: off",
            )
        if action.startswith("admin:jobs"):
            page = max(0, int(action.split(":")[2])) if action.count(":") > 1 else 0
            jobs = await self.db.all("SELECT * FROM jobs ORDER BY id DESC LIMIT 20 OFFSET ?", (page * 20,))
            rows = []
            for job in jobs:
                title = (
                    f"#{job['id']} {job['title']} | {job['kind']} | {job['hours']}h | {'✅' if job['enabled'] else '⏸'}"
                )
                rows.append([await self.button("fa", "", "admin:job:" + str(job["id"]), text=title)])
            total = await self.db.one("SELECT COUNT(*) n FROM jobs")
            nav = []
            if page:
                nav.append(await self.button("fa", "", f"admin:jobs:{page - 1}", text="◀️"))
            if (page + 1) * 20 < total["n"]:
                nav.append(await self.button("fa", "", f"admin:jobs:{page + 1}", text="▶️"))
            if nav:
                rows.append(nav)
            rows.append([await self.button("fa", "", "admin:jobadd", text="➕ زمان‌بندی جدید")])
            return await self.send(uid, f"برنامه‌های کانال · صفحه {page + 1}", rows)
        if action.startswith("admin:job:"):
            jid = int(action.split(":")[2])
            job = await self.db.one("SELECT * FROM jobs WHERE id=?", (jid,))
            if not job:
                return
            text = f"#{jid}\n{job['title']}\n{job['kind']} | {job['sign']} | {job['lang']}\nهر {job['hours']} ساعت\nارسال بعدی UTC: {datetime.fromtimestamp(job['next_due'], ZoneInfo('UTC')).isoformat()}\nخطا: {job['last_error'] or '—'}"
            return await self.send(
                uid,
                html.escape(text),
                [
                    [
                        await self.button("fa", "", f"admin:toggle:{jid}", text="توقف/فعال"),
                        await self.button("fa", "", f"admin:preview:{jid}", text="پیش‌نمایش برای من"),
                    ],
                    [await self.button("fa", "", f"admin:jobdelete:{jid}", text="حذف زمان‌بندی")],
                ],
            )
        if action.startswith(("admin:toggle:", "admin:jobdelete:", "admin:preview:")):
            jid = int(action.split(":")[2])
            async with self.job_lock:
                job = await self.db.one("SELECT * FROM jobs WHERE id=?", (jid,))
                if not job:
                    return
                if ":toggle:" in action:
                    await self.db.execute(
                        "UPDATE jobs SET enabled=1-enabled,next_due=?,retry_at=0 WHERE id=?",
                        (time.time() + job["hours"] * 3600, jid),
                    )
                elif ":jobdelete:" in action:
                    await self.db.execute("DELETE FROM jobs WHERE id=?", (jid,))
                else:
                    from .scheduler import channel_cards

                    for card in await channel_cards(self, job):
                        await self.send(uid, card)
            return await self.admin(uid, "admin:jobs")
        if action == "admin:theme":
            theme = await self.db.setting("theme", {})
            await self.send(uid, html.escape(str(theme)))
            rows = [
                [await self.button("fa", "", "admin:style:" + x, text=label)]
                for x, label in [("primary", "آبی"), ("success", "سبز"), ("danger", "قرمز"), ("default", "پیش‌فرض")]
            ]
            rows += [
                [await self.button("fa", "", "admin:emoji", text="ایموجی پرمیوم دکمه")],
                [await self.button("fa", "", "admin:textemoji", text="ایموجی پرمیوم متن")],
            ]
            return await self.send(uid, "رنگ مجاز تلگرام را انتخاب کن. ایموجی پرمیوم نیاز به مجوز تلگرام دارد.", rows)
        if action.startswith("admin:style:"):
            style = action.split(":")[2]
            if style not in ("primary", "success", "danger", "default"):
                return
            theme = await self.db.setting("theme", {})
            theme["style"] = style
            await self.db.set("theme", theme)
            return await self.admin(uid, "admin:theme")
        if action == "admin:bconfirm":
            draft = await self.db.setting("broadcast_draft:" + str(uid))
            if not draft:
                return
            maximum = await self.db.one("SELECT COALESCE(MAX(id),0) m FROM users")
            jid = await self.db.execute(
                "INSERT INTO broadcasts(text,max_user_id,created) VALUES(?,?,?)", (draft, maximum["m"], time.time())
            )
            await self.db.set("broadcast_draft:" + str(uid), None)
            return await self.send(uid, f"پیام همگانی #{jid} در صف قرار گرفت. وضعیت و توقف از بخش پیام همگانی.")
        if action.startswith("admin:bstop:"):
            await self.db.execute("UPDATE broadcasts SET enabled=0 WHERE id=?", (int(action.split(":")[2]),))
            return await self.send(uid, "ارسال متوقف شد.")
        prompts = {
            "jobadd": "قالب: کانال | فاصله ساعت | نوع | زبان | برج | ساعت اولین ارسال | منطقه زمانی\n<code>@YourChannel | 6 | general | fa | all | 09:00 | Asia/Tehran</code>\nنوع: general (خلاصه ۱۲ برج)، daily، weekly، monthly، yearly، tarot\nبرج: all یا aries تا pisces؛ فاصله ۱ تا ۸۷۶۰ ساعت. اولین ارسال در نوبت ساعت انتخابی انجام می‌شود. ربات باید اجازه ارسال داشته باشد.",
            "labels": "قالب: زبان | کلید | متن\n<code>fa | daily | 🔮 فال امروزم</code>\nکلیدهای قابل ویرایش در README؛ برای حذف سفارشی‌سازی متن را reset بگذار.",
            "welcome": "قالب: زبان | متن شروع\n<code>fa | به ربات فال خوش آمدی ✨</code>",
            "footer": "امضای متن ساده کانال را بفرست. حذف: off",
            "annual": "قالب: سال میلادی | برج | زبان | متن\n<code>2026 | aries | fa | متن فال سالانه ...</code>\nاین متن با عنوان محتوای مدیر منتشر می‌شود؛ API فال سالانه ندارد.",
            "emoji": "شناسه عددی ایموجی سفارشی برای دکمه‌ها را بفرست؛ حذف: off",
            "textemoji": "شناسه عددی ایموجی سفارشی برای متن شروع را بفرست؛ حذف: off",
            "broadcast": "متن ساده پیام همگانی را بفرست؛ ابتدا پیش‌نمایش و سپس تأیید ارسال نمایش داده می‌شود.",
        }
        key = action.removeprefix("admin:")
        if key in prompts:
            if key == "broadcast":
                active = await self.db.all("SELECT id,sent,failed,enabled FROM broadcasts ORDER BY id DESC LIMIT 5")
                for b in active:
                    await self.send(
                        uid,
                        f"#{b['id']} | موفق {b['sent']} | ناموفق {b['failed']} | فعال {b['enabled']}",
                        [[await self.button("fa", "", f"admin:bstop:{b['id']}", text="توقف")]],
                    )
            await self.db.set_state(uid, {"kind": action})
            return await self.send(uid, prompts[key])

    async def resolve_channel(self, raw, require_admin=True):
        raw = raw.strip()
        if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}|-100[0-9]+", raw):
            raise ValueError("شناسه کانال معتبر نیست")
        chat = await self.tg.call("getChat", chat_id=int(raw) if raw.startswith("-") else raw)
        if chat["type"] != "channel":
            raise ValueError("شناسه باید متعلق به کانال باشد")
        member = await self.tg.call("getChatMember", chat_id=chat["id"], user_id=self.bot_id)
        if require_admin and member["status"] not in ("creator", "administrator"):
            raise ValueError("ابتدا ربات را ادمین کانال کن")
        return chat, member

    async def admin_input(self, uid, text, kind):
        if uid not in self.cfg.admins:
            return
        if await self.extra.admin_input(uid, text, kind):
            return
        key = kind.removeprefix("admin:")
        try:
            if key == "members":
                channels = []
                if text.strip().lower() != "off":
                    lines = text.strip().splitlines()
                    if not 1 <= len(lines) <= 10:
                        raise ValueError("حداکثر ۱۰ کانال")
                    for line in lines:
                        fields = list(map(str.strip, line.split("|")))
                        if len(fields) not in (2, 4):
                            raise ValueError("قالب کانال | لینک | نوع هدف | تعداد")
                        raw, url = fields[:2]
                        mode, goal = (
                            ("members", 0) if len(fields) == 2 else (fields[2], int(fields[3].translate(DIGITS)))
                        )
                        if mode not in ("members", "joins") or not 0 <= goal <= 1000000000:
                            raise ValueError("هدف معتبر نیست")
                        if not re.fullmatch(r"https://t\.me/[A-Za-z0-9_+/-]+", url):
                            raise ValueError("لینک عضویت باید https://t.me/ باشد")
                        chat, _ = await self.resolve_channel(raw)
                        if chat["id"] not in [c["id"] for c in channels]:
                            previous = await self.db.setting("required_channels", [])
                            match = next(
                                (
                                    c
                                    for c in previous
                                    if c["id"] == chat["id"]
                                    and c.get("goal_mode", "members") == mode
                                    and c.get("goal", 0) == goal
                                ),
                                None,
                            )
                            epoch = match.get("epoch", "legacy") if match else str(time.time_ns())
                            channels.append(
                                {
                                    "id": chat["id"],
                                    "title": chat["title"],
                                    "url": url,
                                    "goal": goal,
                                    "goal_mode": mode,
                                    "epoch": epoch,
                                }
                            )
                await self.db.set("required_channels", channels)
            elif key == "jobadd":
                raw, hours, mode, lang, sign, clock, zone = map(str.strip, text.split("|"))
                hours = int(hours.translate(DIGITS))
                if (
                    not 1 <= hours <= 8760
                    or mode not in (*PERIODS, "general", "tarot")
                    or lang not in LANGS
                    or sign not in (*SIGNS, "all")
                ):
                    raise ValueError("نوع، زبان، برج یا فاصله معتبر نیست")
                clock, zone = validate_clock(clock + " " + zone)
                chat, member = await self.resolve_channel(raw)
                if member["status"] != "creator" and not member.get("can_post_messages"):
                    raise ValueError("مجوز ارسال به کانال را فعال کن")
                count = await self.db.one("SELECT COUNT(*) n FROM jobs")
                if count["n"] >= 100:
                    raise ValueError("حداکثر ۱۰۰ زمان‌بندی؛ موارد قدیمی را حذف کن")
                await self.db.execute(
                    "INSERT INTO jobs(chat_id,title,hours,kind,lang,sign,next_due) VALUES(?,?,?,?,?,?,?)",
                    (chat["id"], chat["title"], hours, mode, lang, sign, next_delivery(clock, zone)),
                )
            elif key in ("emoji", "textemoji"):
                value = text.strip().translate(DIGITS)
                if value != "off" and not re.fullmatch(r"[0-9]{1,24}", value):
                    raise ValueError("شناسه عددی لازم است")
                theme = await self.db.setting("theme", {})
                theme["emoji" if key == "emoji" else "text_emoji"] = "" if value == "off" else value
                await self.db.set("theme", theme)
            elif key == "labels":
                lang, label, value = map(str.strip, text.split("|", 2))
                if lang not in LANGS or label not in TEXTS["en"] or not 1 <= len(value) <= 64:
                    raise ValueError("زبان یا کلید یا طول متن معتبر نیست")
                labels = await self.db.setting("labels", {})
                if value == "reset":
                    labels.pop(lang + ":" + label, None)
                else:
                    labels[lang + ":" + label] = value
                await self.db.set("labels", labels)
            elif key == "welcome":
                lang, value = map(str.strip, text.split("|", 1))
                if lang not in LANGS or not 1 <= len(value) <= 500:
                    raise ValueError("زبان یا طول متن معتبر نیست")
                await self.db.set("welcome:" + lang, value)
            elif key == "footer":
                if len(text) > 100:
                    raise ValueError("حداکثر ۱۰۰ حرف")
                await self.db.set("footer", "" if text.strip() == "off" else text)
            elif key == "annual":
                year, sign, lang, value = map(str.strip, text.split("|", 3))
                year = int(year.translate(DIGITS))
                if not 1900 <= year <= 2200 or sign not in SIGNS or lang not in LANGS or not 1 <= len(value) <= 8000:
                    raise ValueError("سال، برج، زبان یا طول متن معتبر نیست")
                await self.db.execute("INSERT OR REPLACE INTO annual VALUES(?,?,?,?)", (year, sign, lang, value))
            elif key == "broadcast":
                if not 1 <= len(text) <= 600:
                    raise ValueError("حداکثر ۶۰۰ حرف")
                await self.db.set("broadcast_draft:" + str(uid), text)
                await self.db.set_state(uid)
                return await self.send(
                    uid,
                    "<b>پیش‌نمایش پیام همگانی</b>\n\n" + html.escape(text),
                    [[await self.button("fa", "", "admin:bconfirm", text="تأیید ارسال به کاربران")]]
                    + await self.back("fa"),
                )
            else:
                return
        except (ValueError, KeyError) as exc:
            return await self.send(uid, "ورودی معتبر نیست: " + html.escape(str(exc)) + "\n/cancel")
        except TelegramError:
            return await self.send(uid, "دسترسی کانال تأیید نشد؛ شناسه و ادمین‌بودن ربات را بررسی کن. /cancel")
        await self.db.set_state(uid)
        await self.send(uid, "ذخیره شد ✅", [[await self.button("fa", "", "admin:home", text="پنل مدیریت")]])
