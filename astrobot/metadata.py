"""English default bot metadata with optional Telegram-localized variants."""

from .core import FALLBACK_LANGUAGE, LANGS
from .i18n import t

PROFILE_VERSION = 3
COMMAND_KEYS = (
    ("start", "back"),
    ("today", "daily"),
    ("tarot", "tarot"),
    ("spread", "spread"),
    ("profile", "profile"),
    ("birthdate", "birth"),
    ("daily", "subscribe"),
    ("history", "history"),
    ("rewards", "reward"),
    ("support", "support"),
    ("language", "language"),
    ("privacy", "privacy"),
    ("faq", "faq"),
)


def commands_for(language=FALLBACK_LANGUAGE):
    return [{"command": command, "description": t(language, key)[:200]} for command, key in COMMAND_KEYS]


async def configure_profile(telegram, db):
    # Always refresh the default list, including on upgrades from bilingual v2.
    await telegram.call("setMyCommands", commands=commands_for())
    if await db.setting("profile_version") == PROFILE_VERSION:
        return
    await telegram.call("setMyName", name="Falino ✨")
    await telegram.call(
        "setMyDescription",
        description=(t(FALLBACK_LANGUAGE, "welcome") + "\n" + t(FALLBACK_LANGUAGE, "fun") + "\n/help · /support")[:512],
    )
    await telegram.call("setMyShortDescription", short_description=t(FALLBACK_LANGUAGE, "welcome").split("\n")[0][:120])
    for language in LANGS:
        await telegram.call("setMyCommands", commands=commands_for(language), language_code=language)
        await telegram.call(
            "setMyDescription",
            description=(t(language, "welcome") + "\n" + t(language, "fun") + "\n/help · /support")[:512],
            language_code=language,
        )
        await telegram.call(
            "setMyShortDescription",
            short_description=t(language, "welcome").split("\n")[0][:120],
            language_code=language,
        )
    await db.set("profile_version", PROFILE_VERSION)
