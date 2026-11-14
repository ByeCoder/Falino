from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import jdatetime
from dotenv import load_dotenv

UTC = timezone.utc
FALLBACK_LANGUAGE = "en"
SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)
SYMBOLS = ("♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓")
SIGN_NAMES = {
    "fa": ("حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"),
    "en": tuple(s.title() for s in SIGNS),
    "ar": (
        "الحمل",
        "الثور",
        "الجوزاء",
        "السرطان",
        "الأسد",
        "العذراء",
        "الميزان",
        "العقرب",
        "القوس",
        "الجدي",
        "الدلو",
        "الحوت",
    ),
    "tr": ("Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"),
}
# User-requested display order: Chinese and Hindi first.
LANGS = {
    "zh": "中文",
    "hi": "हिन्दी",
    "fa": "فارسی",
    "ar": "العربية",
    "en": "English",
    "ru": "Русский",
    "he": "עברית",
    "es": "Español",
    "fr": "Français",
    "tr": "Türkçe",
}
SIGN_NAMES.update(
    {
        "zh": (
            "白羊座",
            "金牛座",
            "双子座",
            "巨蟹座",
            "狮子座",
            "处女座",
            "天秤座",
            "天蝎座",
            "射手座",
            "摩羯座",
            "水瓶座",
            "双鱼座",
        ),
        "hi": ("मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"),
        "ru": (
            "Овен",
            "Телец",
            "Близнецы",
            "Рак",
            "Лев",
            "Дева",
            "Весы",
            "Скорпион",
            "Стрелец",
            "Козерог",
            "Водолей",
            "Рыбы",
        ),
        "he": ("טלה", "שור", "תאומים", "סרטן", "אריה", "בתולה", "מאזניים", "עקרב", "קשת", "גדי", "דלי", "דגים"),
        "es": (
            "Aries",
            "Tauro",
            "Géminis",
            "Cáncer",
            "Leo",
            "Virgo",
            "Libra",
            "Escorpio",
            "Sagitario",
            "Capricornio",
            "Acuario",
            "Piscis",
        ),
        "fr": (
            "Bélier",
            "Taureau",
            "Gémeaux",
            "Cancer",
            "Lion",
            "Vierge",
            "Balance",
            "Scorpion",
            "Sagittaire",
            "Capricorne",
            "Verseau",
            "Poissons",
        ),
    }
)


def normalize_language(code):
    code = (code or "").lower().replace("_", "-").split("-")[0]
    return "he" if code == "iw" else code if code in LANGS else FALLBACK_LANGUAGE


PERIODS = ("daily", "weekly", "monthly", "yearly")
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩०१२३४५६७८९", "012345678901234567890123456789")


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    token: str
    admins: frozenset[int]
    data_dir: Path
    llm_url: str = ""
    llm_key: str = ""
    llm_model: str = ""
    http_proxy: str = ""
    mtproxy: str = ""

    @classmethod
    def load(cls):
        load_dotenv()
        missing = [k for k in ("API_ID", "API_HASH", "BOT_TOKEN", "ADMIN_IDS") if not os.getenv(k)]
        if missing:
            raise ValueError("Fill .env first: " + ", ".join(missing))
        admins = frozenset(int(x.strip()) for x in os.environ["ADMIN_IDS"].split(",") if x.strip())
        if not admins or any(x <= 0 for x in admins):
            raise ValueError("ADMIN_IDS must contain positive numeric user IDs")
        return cls(
            int(os.environ["API_ID"]),
            os.environ["API_HASH"],
            os.environ["BOT_TOKEN"],
            admins,
            Path(os.getenv("DATA_DIR", "data")),
            os.getenv("LLM_BASE_URL", ""),
            os.getenv("LLM_API_KEY", ""),
            os.getenv("LLM_MODEL", ""),
            os.getenv("HTTP_PROXY_URL", ""),
            os.getenv("TELETHON_PROXY_URL", ""),
        )


def now_utc():
    return datetime.now(UTC)


def sign_for(born: date) -> str:
    boundaries = (
        (1, 20, "aquarius"),
        (2, 19, "pisces"),
        (3, 21, "aries"),
        (4, 20, "taurus"),
        (5, 21, "gemini"),
        (6, 21, "cancer"),
        (7, 23, "leo"),
        (8, 23, "virgo"),
        (9, 23, "libra"),
        (10, 23, "scorpio"),
        (11, 22, "sagittarius"),
        (12, 22, "capricorn"),
    )
    sign = "capricorn"
    for month, day, name in boundaries:
        if (born.month, born.day) >= (month, day):
            sign = name
    return sign


def sign_label(sign, lang=FALLBACK_LANGUAGE):
    i = SIGNS.index(sign)
    return f"{SYMBOLS[i]} {SIGN_NAMES.get(lang, SIGN_NAMES['en'])[i]}"


def parse_birth(raw: str, calendar: str, today=None) -> date:
    parts = raw.translate(DIGITS).strip().replace("/", "-").split("-")
    if len(parts) != 3:
        raise ValueError("YYYY-MM-DD")
    y, m, d = map(int, parts)
    born = jdatetime.date(y, m, d).togregorian() if calendar == "j" else date(y, m, d)
    if not date(1900, 1, 1) <= born <= (today or now_utc().astimezone(ZoneInfo("Asia/Tehran")).date()):
        raise ValueError("Birth date out of range")
    return born


def next_delivery(clock: str, zone: str, after=None) -> float:
    after = after or now_utc()
    local = after.astimezone(ZoneInfo(zone))
    target = datetime.combine(local.date(), time.fromisoformat(clock), tzinfo=local.tzinfo)
    if target <= local:
        target += timedelta(days=1)
    # A UTC round trip resolves nonexistent wall times on DST transition days.
    return target.astimezone(UTC).timestamp()


def validate_clock(raw):
    clock, zone = raw.translate(DIGITS).strip().split()
    t = time.fromisoformat(clock)
    if t.tzinfo or t.second or t.microsecond:
        raise ValueError("HH:MM Zone")
    ZoneInfo(zone)
    return t.strftime("%H:%M"), zone


def split_text(text: str, limit=2600):
    """Short plain-text blocks; escape only after splitting to preserve HTML entities."""
    while text:
        cut = min(limit, len(text))
        if len(text) > limit:
            newline = text.rfind("\n", 0, cut)
            if newline > limit // 2:
                cut = newline + 1
        yield text[:cut]
        text = text[cut:]
