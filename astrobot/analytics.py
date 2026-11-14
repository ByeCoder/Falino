from __future__ import annotations

import html
import json
import time
from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo

import jdatetime

from .core import now_utc, sign_label

TEHRAN = ZoneInfo("Asia/Tehran")
KIND_NAMES = {
    "daily": "روزانه",
    "weekly": "هفتگی",
    "monthly": "ماهانه",
    "yearly": "سالانه",
    "tarot": "تاروت روز",
    "spread": "تاروت سه‌کارتی",
    "natal": "سیارات تولد",
    "compat": "سازگاری",
    "moon": "فاز ماه",
    "register": "ورود کاربر جدید",
    "profile": "تغییر پروفایل",
    "support": "پیام پشتیبانی",
    "reply": "پاسخ مدیر",
    "feedback": "بازخورد",
    "error": "خطای سرویس",
    "reading": "دریافت فال",
    "referral": "دعوت تأییدشده",
    "claim": "دریافت جایزه",
    "channel": "ارسال کانال",
}


def calendar_windows(now=None):
    local = (now or now_utc()).astimezone(TEHRAN)
    day = local.date()
    saturday = day - timedelta(days=(day.weekday() + 2) % 7)
    jalali = jdatetime.date.fromgregorian(date=day)
    month = jdatetime.date(jalali.year, jalali.month, 1).togregorian()
    return {"daily": day.isoformat(), "weekly": saturday.isoformat(), "monthly": month.isoformat(), "all": "0001-01-01"}


async def profile_text(db, uid):
    u = await db.user(uid)
    if not u:
        return "کاربر دیگر در ربات نیست."

    def safe(value):
        return html.escape(str(value if value not in (None, "") else "—"))

    def stamp(value):
        return datetime.fromtimestamp(value, TEHRAN).strftime("%Y-%m-%d %H:%M") if value else "—"

    refs = await db.one("SELECT COUNT(*) n FROM users WHERE referred_by=?", (uid,))
    verified = await db.one("SELECT COUNT(*) n FROM users WHERE referred_by=? AND ref_rewarded=1", (uid,))
    lines = [
        f'<a href="tg://user?id={uid}"><b>{safe(u["name"])} {safe(u["last_name"])}</b></a>',
        f"شناسه: <code>{uid}</code>",
        f"نام کاربری: {safe('@' + u['username'] if u['username'] else '—')}",
        f"نام دلخواه: {safe(u.get('nickname'))}",
        f"زبان ربات: {safe(u['lang'])} | زبان تلگرام: {safe(u['telegram_lang'])}",
        f"پرمیوم تلگرام: {'بله' if u['premium'] else 'خیر/اعلام‌نشده'}",
        f"تولد میلادی: {safe(u['birth'])}",
        f"برج: {safe(sign_label(u['sign'], 'fa') if u['sign'] else '—')}",
        f"دریافت روزانه: {'فعال' if u['subscribed'] else 'خاموش'} | {safe(u['clock'])} {safe(u['zone'])}",
        f"عضویت: {stamp(u['created'])}",
        f"آخرین فعالیت: {stamp(u['last_seen'])}",
        f"امتیاز: {u['points']} | زنجیره: {u['streak']} | رکورد: {u['best_streak']}",
        f"معرف: {safe(u['referred_by'])} | منبع: {safe(u['source'])}",
        f"دعوت: {refs['n']} | تأییدشده: {verified['n']}",
        f"محدودشده توسط مدیر: {'بله' if u['banned'] else 'خیر'} | مسدودکننده ربات: {'بله' if u['blocked'] else 'خیر'}",
    ]
    return "\n".join(lines)


class Analytics:
    def __init__(self, app):
        self.app = app

    async def record(self, uid, kind, detail="", sign="", source="", audit=True):
        db = self.app.db
        stamp = time.time()
        day = datetime.fromtimestamp(stamp, TEHRAN).date().isoformat()
        statements = [
            (
                "INSERT INTO events(user_id,kind,detail,sign,source,created) VALUES(?,?,?,?,?,?)",
                (uid, kind, detail, sign, source, stamp),
            ),
            (
                "INSERT INTO metric_days VALUES(?,?,?,1) ON CONFLICT(day,kind,detail) DO UPDATE SET count=count+1",
                (day, kind, detail),
            ),
        ]
        if uid is not None:
            statements.append(("INSERT OR IGNORE INTO active_days VALUES(?,?)", (day, uid)))
        result = await db.batch(statements)
        if audit and uid is not None:
            group = await db.setting("log_group")
            if group:
                n = await db.one("SELECT COUNT(*) n FROM outbox WHERE kind='audit'")
                if n["n"] < 5000:
                    title = KIND_NAMES.get(kind, kind) + " · " + KIND_NAMES.get(detail, detail)
                    text = f"<b>📌 {html.escape(title)}</b>\n{datetime.fromtimestamp(stamp, TEHRAN).strftime('%Y-%m-%d %H:%M')}\n\n"
                    text += await profile_text(db, uid)
                    if sign:
                        text += "\nفال انتخاب‌شده: " + html.escape(sign)
                    text += "\nمسیر: " + html.escape(source or "private")
                    await db.execute(
                        "INSERT INTO outbox(user_id,kind,chat_id,payload,created) VALUES(?,?,?,?,?)",
                        (uid, "audit", group, json.dumps({"text": text}, ensure_ascii=False), stamp),
                    )
        return result[0][0]

    async def report(self, period="all"):
        db = self.app.db
        start = calendar_windows().get(period)
        if start is None:
            raise ValueError("Unknown reporting period")
        rows = await db.all(
            "SELECT kind,detail,SUM(count) n FROM metric_days WHERE day>=? GROUP BY kind,detail", (start,)
        )
        totals = {}
        readings = []
        for r in rows:
            totals[r["kind"]] = totals.get(r["kind"], 0) + r["n"]
            if r["kind"] == "reading":
                readings.append(f"  {KIND_NAMES.get(r['detail'], r['detail'])}: {r['n']}")
        active = await db.one("SELECT COUNT(DISTINCT user_id) n FROM active_days WHERE day>=?", (start,))
        current = await db.one(
            "SELECT COUNT(*) total,SUM(subscribed) subs,SUM(blocked) blocked,SUM(banned) banned FROM users"
        )
        ratings = await db.one(
            "SELECT SUM(rating=1) good,SUM(rating=0) bad FROM history WHERE rating IS NOT NULL AND created>=?",
            (
                datetime.combine(datetime.fromisoformat(start).date(), dtime(), tzinfo=TEHRAN).timestamp()
                if period != "all"
                else 0,
            ),
        )
        names = {"daily": "امروز", "weekly": "این هفته از شنبه", "monthly": "این ماه شمسی", "all": "همه زمان‌ها"}
        since = await db.setting("analytics_since", time.time())
        text = (
            f"<b>📊 فالینو · {names[period]}</b>\nمبنای زمان: تهران\nاز {start if period != 'all' else 'شروع ثبت'}\n\n"
        )
        text += f"👋 ثبت‌نام: {totals.get('register', 0)}\n👥 کاربر فعال یکتا: {active['n']}\n🔮 دریافت موفق فال: {totals.get('reading', 0)}\n"
        text += "\n".join(readings)
        text += f"\n💬 پیام پشتیبانی: {totals.get('support', 0)}\n📨 پاسخ مدیر: {totals.get('reply', 0)}\n🫶 دعوت تأییدشده: {totals.get('referral', 0)}\n📢 نوبت موفق کانال: {totals.get('channel', 0)}\n⚠️ خطاها: {totals.get('error', 0)}\n"
        text += f"\nوضعیت فعلی کل ربات:\nکاربران: {current['total']}\nاشتراک روزانه: {current['subs'] or 0}\nمسدودکننده ربات: {current['blocked'] or 0}\nمحدودشده: {current['banned'] or 0}\n"
        text += f"بازخوردهای ذخیره‌شده: 👍 {ratings['good'] or 0} / 👎 {ratings['bad'] or 0}\n"
        sources = await db.all(
            "SELECT COALESCE(source,'direct') source,COUNT(*) n FROM users WHERE created>=? GROUP BY source ORDER BY n DESC LIMIT 5",
            (
                datetime.combine(datetime.fromisoformat(start).date(), dtime(), tzinfo=TEHRAN).timestamp()
                if period != "all"
                else 0,
            ),
        )
        text += "\nمنابع ثبت‌نام فعلی:\n" + "\n".join(html.escape(f"{r['source']}: {r['n']}") for r in sources)
        text += "\n\nثبت جزئیات فعالیت از " + datetime.fromtimestamp(since, TEHRAN).strftime("%Y-%m-%d %H:%M")
        return text
