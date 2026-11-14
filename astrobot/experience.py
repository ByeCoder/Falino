from __future__ import annotations

import html
import json
import re
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .analytics import Analytics, calendar_windows, profile_text
from .core import DIGITS, SIGNS, now_utc, sign_label
from .i18n import t
from .services import TelegramError
from .support import Support


class Experience:
    def __init__(self, app):
        self.app = app
        self.analytics = Analytics(app)
        self.support = Support(app, self.analytics)

    async def visit(self, uid, new=False):
        app = self.app
        u = await app.db.user(uid)
        day = now_utc().astimezone(ZoneInfo(u["zone"])).date()
        if new:
            await self.analytics.record(uid, "register", source=u["source"] or "direct")
        await self.analytics.record(uid, "visit", audit=False)
        if u["streak_day"] != day.isoformat():
            previous = date.fromisoformat(u["streak_day"]) if u["streak_day"] else None
            # Timezone changes cannot increase the streak more than once per UTC day.
            recent = await app.db.one(
                "SELECT created FROM events WHERE user_id=? AND kind='streak' ORDER BY id DESC LIMIT 1", (uid,)
            )
            if not recent or time.time() - recent["created"] >= 20 * 3600:
                streak = u["streak"] + 1 if previous == day - timedelta(days=1) else 1
                await app.db.execute(
                    "UPDATE users SET streak=?,best_streak=MAX(best_streak,?),streak_day=? WHERE id=?",
                    (streak, streak, day.isoformat(), uid),
                )
                await self.analytics.record(uid, "streak", audit=False)

    async def save_history(self, uid, kind, sign, lang, cards):
        stored = []
        length = 0
        for card in cards:
            if length + len(card) > 24000:
                break
            stored.append(card)
            length += len(card)
        return await self.app.db.execute(
            "INSERT INTO history(user_id,kind,sign,lang,cards,created) VALUES(?,?,?,?,?,?)",
            (uid, kind, sign or "", lang, json.dumps(stored, ensure_ascii=False), time.time()),
        )

    async def completed(self, uid, kind, sign="", source="private", history_id=None):
        app = self.app
        if history_id:
            await app.db.execute("UPDATE history SET delivered=1 WHERE id=? AND user_id=?", (history_id, uid))
        await self.analytics.record(uid, "reading", kind, sign, source)
        u = await app.db.user(uid)
        if not u:
            return
        day = now_utc().astimezone(ZoneInfo(u["zone"])).date().isoformat()
        if kind == "daily":
            await app.db.execute("INSERT OR IGNORE INTO reward_days VALUES(?,?,?)", (uid, day, "daily_read"))
        if kind == "tarot":
            key = f"tarot:{uid}:{now_utc().date().isoformat()}"
            card = await app.db.cached(key)
            if card:
                await app.db.execute(
                    "INSERT OR IGNORE INTO card_collection VALUES(?,?,?)",
                    (uid, card.get("name", card.get("name_short", "?")), time.time()),
                )
        if u["birth"] and u["referred_by"] and not u["ref_rewarded"] and kind == "daily":
            # Existing accounts never change attribution. Reward only after a completed
            # birth profile and a successful daily reading, once per invitee.
            token = await app.db.abuse_token(uid)
            result = await app.db.batch(
                [
                    ("INSERT OR IGNORE INTO anti_abuse VALUES(?,?,?)", ("referral", token, time.time())),
                    ("UPDATE users SET points=points+30 WHERE id=? AND changes()=1", (u["referred_by"],)),
                    ("UPDATE users SET ref_rewarded=1 WHERE id=?", (uid,)),
                ]
            )
            if result[0][1] and await app.db.user(u["referred_by"]):
                await self.analytics.record(u["referred_by"], "referral", source="qualified_profile")
        await app.db.execute(
            "DELETE FROM history WHERE user_id=? AND favorite=0 AND id NOT IN (SELECT id FROM history WHERE user_id=? ORDER BY id DESC LIMIT 30)",
            (uid, uid),
        )

    async def reading_buttons(self, uid, hid, lang):
        app = self.app
        return [
            [
                await app.button(lang, "favorite", f"hfav:{hid}"),
                await app.button(lang, "", f"rate:{hid}:1", text="👍"),
                await app.button(lang, "", f"rate:{hid}:0", text="👎"),
            ]
        ]

    async def public_route(self, uid, user, text, callback, context=None):
        app = self.app
        lang = user["lang"]
        cmd = text.split(maxsplit=1)[0].split("@")[0] if text.strip() else ""
        if cmd == "/privacy" or callback == "privacy":
            await app.send(uid, html.escape(t(lang, "privacy_text")), await app.back(lang))
            return True
        if cmd in ("/support", "/feedback") or callback == "support":
            await app.db.set_state(uid, {"kind": "x:support"})
            await app.send(uid, html.escape(t(lang, "support_prompt")), await app.back(lang))
            return True
        if cmd == "/tickets" or callback == "tickets":
            tickets = await app.db.all(
                "SELECT id,status,updated FROM tickets WHERE user_id=? ORDER BY id DESC LIMIT 10", (uid,)
            )
            rows = [
                [
                    await app.button(
                        lang,
                        "",
                        f"uticket:{row['id']}",
                        text=f"#{row['id']} · {t(lang, 'ticket_open_label' if row['status'] == 'open' else 'ticket_closed_label')}",
                    )
                ]
                for row in tickets
            ]
            await app.send(
                uid, html.escape(t(lang, "tickets") if tickets else t(lang, "no_items")), rows + await app.back(lang)
            )
            return True
        if callback and callback.startswith("uticket:"):
            tid = int(callback.split(":")[1])
            ticket = await app.db.one("SELECT * FROM tickets WHERE id=? AND user_id=?", (tid, uid))
            if ticket:
                messages = await app.db.all(
                    "SELECT role,text FROM ticket_messages WHERE ticket_id=? AND role!='internal' ORDER BY id DESC LIMIT 6",
                    (tid,),
                )
                for m in reversed(messages):
                    for i in range(0, len(m["text"]), 450):
                        await app.send(
                            uid,
                            html.escape(
                                f"{t(lang, 'role_user' if m['role'] == 'user' else 'role_staff')}: {m['text'][i : i + 450]}"
                            ),
                        )
                await app.send(
                    uid,
                    f"#{tid} · {t(lang, 'ticket_open_label' if ticket['status'] == 'open' else 'ticket_closed_label')}",
                    [
                        [
                            await app.button(lang, "support", "support"),
                            await app.button(lang, "", f"uclose:{tid}", text="🔒"),
                        ]
                    ],
                )
            return True
        if callback and callback.startswith("uclose:"):
            await self.support.close(uid, int(callback.split(":")[1]))
            return True
        state = await app.db.state(uid)
        if state and state["kind"] == "x:support" and not callback and not text.startswith("/"):
            await self.support.submit(uid, text, context)
            return True
        return False

    async def route(self, uid, user, text, callback):
        app = self.app
        lang = user["lang"]
        cmd = text.split(maxsplit=1)[0].split("@")[0] if text.strip() else ""
        if callback == "explore":
            keys = [
                "yearly",
                "favorites",
                "streak",
                "quests",
                "collection",
                "partners",
                "moon",
                "mood",
                "natal",
                "tickets",
                "faq",
                "privacy",
            ]
            buttons = [await app.button(lang, k, k if k != "yearly" else "p:yearly") for k in keys]
            await app.send(
                uid,
                html.escape(t(lang, "explore")),
                [buttons[i : i + 2] for i in range(0, len(buttons), 2)] + await app.back(lang),
            )
            return True
        if cmd == "/faq" or callback == "faq":
            await app.send(uid, html.escape(t(lang, "faq_text")), await app.back(lang))
            return True
        if cmd in ("/history", "/favorites") or callback in ("history", "favorites"):
            await self.history(uid, lang, favorites=(cmd == "/favorites" or callback == "favorites"))
            return True
        if callback and callback.startswith("hpage:"):
            _, page, fav = callback.split(":")
            await self.history(uid, lang, bool(int(fav)), max(0, int(page)))
            return True
        if callback and callback.startswith(("hview:", "hfav:", "rate:")):
            fields = callback.split(":")
            row = await app.db.one(
                "SELECT * FROM history WHERE id=? AND user_id=? AND delivered=1", (int(fields[1]), uid)
            )
            if not row:
                await app.send(uid, html.escape(t(lang, "no_items")))
                return True
            if fields[0] == "hview":
                for card in json.loads(row["cards"]):
                    await app.send(uid, card)
                await app.send(
                    uid,
                    html.escape(t(lang, "feedback")),
                    await self.reading_buttons(uid, row["id"], lang) + await app.back(lang),
                )
                await self.analytics.record(uid, "reading", row["kind"], row["sign"], "history")
            elif fields[0] == "hfav":
                count = await app.db.one("SELECT COUNT(*) n FROM history WHERE user_id=? AND favorite=1", (uid,))
                if not row["favorite"] and count["n"] >= 20:
                    await app.send(uid, html.escape(t(lang, "limited")))
                    return True
                await app.db.execute("UPDATE history SET favorite=1-favorite WHERE id=?", (row["id"],))
                await app.send(uid, html.escape(t(lang, "saved")))
            else:
                rating = int(fields[2])
                if rating not in (0, 1):
                    return True
                await app.db.execute("UPDATE history SET rating=? WHERE id=?", (rating, row["id"]))
                await self.analytics.record(uid, "feedback", str(rating), audit=False)
                await app.send(uid, html.escape(t(lang, "liked" if rating else "disliked")))
            return True
        if cmd == "/name" or callback == "name":
            await app.db.set_state(uid, {"kind": "x:name"})
            await app.send(uid, html.escape(t(lang, "name_prompt")), await app.back(lang))
            return True
        if cmd in ("/streak", "/rewards", "/quests") or callback in (
            "streak",
            "rewards",
            "quests",
            "claim:daily",
            "claim:quest",
            "claim:weekly",
        ):
            if callback and callback.startswith("claim:"):
                await self.claim(uid, callback.split(":")[1])
            else:
                await self.rewards(uid, lang)
            return True
        if cmd == "/collection" or callback == "collection":
            rows = await app.db.all("SELECT card FROM card_collection WHERE user_id=? ORDER BY created DESC", (uid,))
            names = "\n".join(html.escape(r["card"]) for r in rows)
            await app.send(
                uid,
                f"<b>{html.escape(t(lang, 'collection'))} · {len(rows)}/78</b>\n\n"
                + (names or html.escape(t(lang, "no_items"))),
                await app.back(lang),
            )
            return True
        if cmd == "/spread" or callback == "spread":
            cards = await app.horo.spread(uid, lang)
            hid = await self.save_history(uid, "spread", "", lang, cards)
            for card in cards:
                await app.send(uid, card)
            await self.completed(uid, "spread", history_id=hid)
            await app.send(
                uid, html.escape(t(lang, "feedback")), await self.reading_buttons(uid, hid, lang) + await app.back(lang)
            )
            return True
        if cmd == "/partners" or callback == "partners":
            partners = await app.db.all("SELECT * FROM partners WHERE user_id=? ORDER BY id DESC LIMIT 5", (uid,))
            rows = []
            for p in partners:
                prefix = f"compat2:{user['sign']}:{p['sign']}" if user["sign"] else f"compat1:{p['sign']}"
                rows.append(
                    [
                        await app.button(lang, "", prefix, text=p["name"] + " · " + sign_label(p["sign"], lang)),
                        await app.button(lang, "", f"pdelete:{p['id']}", text="🗑"),
                    ]
                )
            rows.append([await app.button(lang, "", "padd", text="➕")])
            await app.send(uid, html.escape(t(lang, "partners")), rows + await app.back(lang))
            return True
        if callback == "padd":
            await app.db.set_state(uid, {"kind": "x:partner"})
            await app.send(uid, html.escape(t(lang, "partner_prompt")), await app.back(lang))
            return True
        if callback and callback.startswith("pdelete:"):
            await app.db.execute("DELETE FROM partners WHERE id=? AND user_id=?", (int(callback.split(":")[1]), uid))
            await app.send(uid, html.escape(t(lang, "saved")), await app.back(lang))
            return True
        state = await app.db.state(uid)
        if state and state["kind"].startswith("x:") and not callback and not text.startswith("/"):
            return await self.input(uid, user, text, state)
        return False

    async def input(self, uid, user, text, state):
        app = self.app
        lang = user["lang"]
        try:
            if state["kind"] == "x:name":
                if not 1 <= len(text.strip()) <= 40:
                    raise ValueError()
                await app.db.execute("UPDATE users SET nickname=? WHERE id=?", (text.strip(), uid))
                await self.analytics.record(uid, "profile", "nickname")
            elif state["kind"] == "x:partner":
                name, sign = map(str.strip, re.split(r"[/|]", text, maxsplit=1))
                count = await app.db.one("SELECT COUNT(*) n FROM partners WHERE user_id=?", (uid,))
                if sign not in SIGNS or not 1 <= len(name) <= 30 or count["n"] >= 5:
                    raise ValueError()
                await app.db.execute("INSERT INTO partners(user_id,name,sign) VALUES(?,?,?)", (uid, name, sign))
            else:
                return False
        except (ValueError, TypeError):
            await app.send(uid, html.escape(t(lang, "invalid")))
            return True
        await app.db.set_state(uid)
        await app.send(uid, html.escape(t(lang, "saved")), await app.back(lang))
        return True

    async def history(self, uid, lang, favorites=False, page=0):
        app = self.app
        rows = await app.db.all(
            "SELECT id,kind,sign,created,favorite FROM history WHERE user_id=? AND delivered=1 AND (?=0 OR favorite=1) ORDER BY id DESC LIMIT 15 OFFSET ?",
            (uid, int(favorites), page * 15),
        )
        buttons = []
        for row in rows:
            stamp = datetime.fromtimestamp(row["created"], ZoneInfo("Asia/Tehran")).strftime("%m-%d")
            text = f"{'⭐ ' if row['favorite'] else ''}{t(lang, row['kind'])} · {stamp}"
            buttons.append([await app.button(lang, "", f"hview:{row['id']}", text=text)])
        total = await app.db.one(
            "SELECT COUNT(*) n FROM history WHERE user_id=? AND delivered=1 AND (?=0 OR favorite=1)",
            (uid, int(favorites)),
        )
        navigation = []
        if page > 0:
            navigation.append(await app.button(lang, "", f"hpage:{page - 1}:{int(favorites)}", text="◀️"))
        if (page + 1) * 15 < total["n"]:
            navigation.append(await app.button(lang, "", f"hpage:{page + 1}:{int(favorites)}", text="▶️"))
        if navigation:
            buttons.append(navigation)
        await app.send(
            uid,
            html.escape(t(lang, "favorites" if favorites else "history") if rows else t(lang, "no_items")),
            buttons + await app.back(lang),
        )

    async def rewards(self, uid, lang):
        app = self.app
        u = await app.db.user(uid)
        day = now_utc().astimezone(ZoneInfo(u["zone"])).date().isoformat()
        done = await app.db.all("SELECT kind FROM reward_days WHERE user_id=? AND day=?", (uid, day))
        kinds = {r["kind"] for r in done}
        mood = await app.db.one("SELECT 1 FROM moods WHERE user_id=? AND day=?", (uid, day))
        text = f"✨ {u['points']} {t(lang, 'points')}\n🔥 {u['streak']} {t(lang, 'days')}\n🏅 {t(lang, 'record')}: {u['best_streak']}\n\n"
        text += t(lang, "daily_task") + f" {'✅' if 'daily_read' in kinds and mood else '◻️'}\n"
        text += t(lang, "weekly_task") + "\n\n" + t(lang, "reward_note")
        rows = [
            [await app.button(lang, "claim", "claim:daily")],
            [
                await app.button(lang, "quests", "claim:quest"),
                await app.button(lang, "", "claim:weekly", text="🏅 +20"),
            ],
            [await app.button(lang, "ref", "ref")],
        ]
        await app.send(uid, html.escape(text), rows + await app.back(lang))

    async def claim(self, uid, kind):
        app = self.app
        u = await app.db.user(uid)
        lang = u["lang"]
        local = now_utc().astimezone(ZoneInfo(u["zone"])).date()
        day = local.isoformat()
        ledger_day = now_utc().date().isoformat()  # timezone changes cannot farm free points.
        points = {"daily": 5, "quest": 10, "weekly": 20}.get(kind)
        if points is None:
            return
        if kind == "quest":
            read = await app.db.one(
                "SELECT 1 FROM reward_days WHERE user_id=? AND day=? AND kind='daily_read'", (uid, day)
            )
            mood = await app.db.one("SELECT 1 FROM moods WHERE user_id=? AND day=?", (uid, day))
            if not (read and mood):
                await app.send(uid, html.escape(t(lang, "daily_task")))
                return
        if kind == "weekly":
            start = calendar_windows()["weekly"]
            visits = await app.db.one(
                "SELECT COUNT(DISTINCT day) n FROM active_days WHERE user_id=? AND day>=?", (uid, start)
            )
            if visits["n"] < 3:
                await app.send(uid, html.escape(t(lang, "weekly_task")))
                return
            ledger_day = start
        result = await app.db.batch(
            [
                ("INSERT OR IGNORE INTO reward_days VALUES(?,?,?)", (uid, ledger_day, "claim_" + kind)),
                ("UPDATE users SET points=points+? WHERE id=? AND changes()=1", (points, uid)),
            ]
        )
        if result[0][1] == 0:
            await app.send(uid, html.escape(t(lang, "claimed")))
        else:
            await self.analytics.record(uid, "claim", kind, audit=False)
            await app.send(uid, f"✨ +{points} " + html.escape(t(lang, "points")))
        await self.rewards(uid, lang)

    async def admin(self, uid, action):
        app = self.app
        if uid not in app.cfg.admins:
            return False
        if action.startswith("admin:stats"):
            period = action.split(":")[2] if action.count(":") > 1 else "all"
            text = await self.analytics.report(period)
            rows = [
                [
                    await app.button("fa", "", f"admin:stats:{key}", text=label)
                    for key, label in [("daily", "روزانه"), ("weekly", "هفتگی")]
                ],
                [
                    await app.button("fa", "", f"admin:stats:{key}", text=label)
                    for key, label in [("monthly", "ماهانه"), ("all", "کلی")]
                ],
            ]
            await app.send(uid, text, rows)
            return True
        if action in ("admin:users", "admin:loggroup", "admin:supportgroup", "admin:campaigns"):
            prompts = {
                "admin:users": "شناسه عددی کاربر، @username یا بخشی از نام او را بفرست.",
                "admin:loggroup": "ربات را ادمین یک گروه خصوصی کن. /chatid را در گروه بزن و شناسه عددی را اینجا بفرست. حذف: off\nاطلاعات کاربران و نوع فال دریافت‌شده به این گروه می‌رود.",
                "admin:supportgroup": "شناسه گروه خصوصی پشتیبانی را بفرست. ربات باید ادمین باشد. در گروه به کارت تیکت Reply کن تا پاسخ به خصوصی کاربر برسد. حذف: off؛ در این صورت تیکت برای مدیران خصوصی می‌آید.",
                "admin:campaigns": "کد کمپین | نام دلخواه\nنمونه: instagram | اینستاگرام\nلینک کمپین و شمار ثبت‌نام‌ها نمایش داده می‌شود.",
            }
            if action == "admin:campaigns":
                rows = await app.db.all(
                    "SELECT c.code,c.title,COUNT(u.id) n FROM campaigns c LEFT JOIN users u ON u.source=c.code GROUP BY c.code ORDER BY c.created DESC LIMIT 10"
                )
                if rows:
                    await app.send(uid, html.escape("\n".join(f"{r['title']}: {r['n']}" for r in rows)))
            await app.db.set_state(uid, {"kind": action})
            await app.send(uid, prompts[action])
            return True
        if action.startswith("admin:user:"):
            target = int(action.split(":")[2])
            u = await app.db.user(target)
            if not u:
                await app.send(uid, "کاربر پیدا نشد.")
                return True
            await app.send(
                uid,
                await profile_text(app.db, target),
                [
                    [
                        await app.button("fa", "", f"admin:uhistory:{target}", text="فال‌های اخیر"),
                        await app.button("fa", "", f"admin:uban:{target}", text="رفع/اعمال محدودیت"),
                    ]
                ],
            )
            return True
        if action.startswith("admin:uhistory:"):
            target = int(action.split(":")[2])
            rows = await app.db.all(
                "SELECT kind,sign,created FROM history WHERE user_id=? AND delivered=1 ORDER BY id DESC LIMIT 15",
                (target,),
            )
            await app.send(
                uid,
                html.escape(
                    "\n".join(
                        f"{r['kind']} | {r['sign']} | {datetime.fromtimestamp(r['created'], ZoneInfo('Asia/Tehran')).strftime('%m-%d %H:%M')}"
                        for r in rows
                    )
                    or "هنوز فالی ثبت نشده."
                ),
            )
            return True
        if action.startswith("admin:uban:"):
            target = int(action.split(":")[2])
            if target in app.cfg.admins:
                await app.send(uid, "مدیر را نمی‌توان محدود کرد.")
            else:
                await app.db.execute(
                    "UPDATE users SET subscribed=CASE WHEN banned=0 THEN 0 ELSE subscribed END,banned=1-banned WHERE id=?",
                    (target,),
                )
                await self.admin(uid, f"admin:user:{target}")
            return True
        if action.startswith("admin:tickets"):
            page = max(0, int(action.split(":")[2])) if action.count(":") > 1 else 0
            rows = await app.db.all(
                "SELECT t.*,u.name FROM tickets t JOIN users u ON u.id=t.user_id ORDER BY (status='open') DESC,updated DESC LIMIT 20 OFFSET ?",
                (page * 20,),
            )
            buttons = [
                [
                    await app.button(
                        "fa", "", f"admin:ticket:{r['id']}", text=f"#{r['id']} · {r['name']} · {r['status']}"
                    )
                ]
                for r in rows
            ]
            total = await app.db.one("SELECT COUNT(*) n FROM tickets")
            nav = []
            if page:
                nav.append(await app.button("fa", "", f"admin:tickets:{page - 1}", text="◀️"))
            if (page + 1) * 20 < total["n"]:
                nav.append(await app.button("fa", "", f"admin:tickets:{page + 1}", text="▶️"))
            if nav:
                buttons.append(nav)
            await app.send(uid, f"💬 صندوق پشتیبانی · صفحه {page + 1}", buttons)
            return True
        if action.startswith("admin:ticket:"):
            await self.support.show_ticket(uid, int(action.split(":")[2]))
            return True
        if action.startswith("admin:treply:"):
            tid = int(action.split(":")[2])
            await app.db.set_state(uid, {"kind": "admin:reply", "ticket": tid})
            await app.send(uid, f"پاسخ تیکت #{tid} را بفرست. /cancel")
            return True
        if action.startswith("admin:tclose:"):
            await self.support.close(uid, int(action.split(":")[2]))
            return True
        return False

    async def admin_input(self, uid, text, kind):
        app = self.app
        if uid not in app.cfg.admins:
            return False
        try:
            if kind == "admin:reply":
                state = await app.db.state(uid)
                if state and await self.support.reply(uid, state["ticket"], text):
                    await app.db.set_state(uid)
                return True
            if kind == "admin:users":
                query = text.strip().translate(DIGITS)
                if query.isdigit():
                    return await self.admin(uid, "admin:user:" + query)
                if query.startswith("@"):
                    rows = await app.db.all(
                        "SELECT id,name,username FROM users WHERE lower(username)=lower(?) LIMIT 15", (query[1:],)
                    )
                else:
                    rows = await app.db.all(
                        "SELECT id,name,username FROM users WHERE instr(lower(name||' '||last_name),lower(?))>0 ORDER BY last_seen DESC LIMIT 15",
                        (query,),
                    )
                await app.send(
                    uid,
                    "نتیجه جست‌وجو",
                    [
                        [await app.button("fa", "", f"admin:user:{r['id']}", text=f"{r['name']} · {r['id']}")]
                        for r in rows
                    ],
                )
            elif kind in ("admin:loggroup", "admin:supportgroup"):
                key = "log_group" if kind == "admin:loggroup" else "support_group"
                if text.strip() == "off":
                    await app.db.set(key, None)
                else:
                    chatid = int(text.translate(DIGITS).strip())
                    if chatid >= 0:
                        raise ValueError("شناسه گروه باید منفی باشد")
                    chat = await app.tg.call("getChat", chat_id=chatid)
                    if chat.get("type") not in ("group", "supergroup") or chat.get("username"):
                        raise ValueError("یک گروه خصوصی برای تیم انتخاب کن")
                    member = await app.tg.call("getChatMember", chat_id=chatid, user_id=app.bot_id)
                    if member.get("status") not in ("creator", "administrator"):
                        raise ValueError("ربات باید در گروه ادمین باشد")
                    await app.send(chatid, "✅ فالینو به این گروه متصل شد. دسترسی پاسخ‌گویی فقط برای ADMIN_IDS است.")
                    await app.db.set(key, chatid)
            elif kind == "admin:campaigns":
                code, title = map(str.strip, text.split("|", 1))
                if not re.fullmatch(r"[A-Za-z0-9_]{1,32}", code) or not 1 <= len(title) <= 50:
                    raise ValueError("کد انگلیسی تا ۳۲ حرف و عنوان تا ۵۰ حرف")
                await app.db.execute(
                    "INSERT INTO campaigns VALUES(?,?,?) ON CONFLICT(code) DO UPDATE SET title=excluded.title",
                    (code, title, time.time()),
                )
                await app.send(uid, f"https://t.me/{app.username}?start=src_{code}")
            else:
                return False
        except (ValueError, TelegramError) as exc:
            await app.send(
                uid,
                "ورودی یا دسترسی معتبر نیست. "
                + (html.escape(str(exc)) if isinstance(exc, ValueError) else "ادمین بودن ربات را بررسی کن."),
            )
            return True
        await app.db.set_state(uid)
        await app.send(uid, "ذخیره شد ✅")
        return True
