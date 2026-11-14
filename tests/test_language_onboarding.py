import pytest

from astrobot.core import LANGS
from astrobot.i18n import t
from astrobot.metadata import PROFILE_VERSION, commands_for, configure_profile


@pytest.mark.parametrize("telegram_language", ["fa", "zh-hans", "hi-IN", "ar", "fr", None])
async def test_first_start_requires_language_selection(app, db, telegram_language):
    await app.dispatch(2, "New user", telegram_language, text="/start")
    user = await db.user(2)
    assert user["lang"] == "" and user["language_selected"] == 0
    assert user["telegram_lang"] == (telegram_language or "")
    rows = app.tg.messages[-1][2]
    assert [row[0]["callback_data"] for row in rows] == ["lang:" + code for code in LANGS]
    assert rows[0][0]["text"] == "中文" and rows[1][0]["text"] == "हिन्दी"
    assert not any(t("en", "welcome") in message[1] for message in app.tg.messages)


async def test_reading_is_blocked_until_language_is_chosen(app, db):
    await app.dispatch(2, "New user", "fa", text="/start")
    await db.execute("UPDATE users SET sign='aries' WHERE id=2")
    await app.dispatch(2, "New user", "fa", text="/today")
    assert not await db.one("SELECT 1 FROM events WHERE kind='reading'")
    assert app.tg.messages[-1][2][0][0]["callback_data"] == "lang:zh"


async def test_explicit_choice_is_saved_and_is_not_overridden_by_telegram_locale(app, db):
    await app.dispatch(2, "New user", "fa", text="/start")
    app.clicks.clear()
    await app.dispatch(2, "New user", "fa", callback="lang:fr")
    await app.dispatch(2, "New user", "zh-hans", text="/start")
    user = await db.user(2)
    assert user["lang"] == "fr" and user["language_selected"] == 1
    assert any(t("fr", "welcome") in message[1] for message in app.tg.messages)
    scoped = [
        p
        for method, p in app.tg.calls
        if method == "setMyCommands" and p.get("scope") == {"type": "chat", "chat_id": 2}
    ]
    assert scoped[-1]["commands"] == commands_for("fr")


async def test_new_database_users_have_no_implicit_language(db):
    await db.touch(2, "New user")
    assert (await db.user(2))["lang"] == ""
    assert (await db.user(2))["language_selected"] == 0


async def test_privacy_remains_available_before_language_choice(app, db):
    await app.dispatch(2, "New user", "fa", text="/start")
    await app.dispatch(2, "New user", "fa", text="/privacy")
    assert any("We store" in message[1] for message in app.tg.messages)
    assert (await db.user(2))["language_selected"] == 0


async def test_english_global_metadata_does_not_select_the_user_language(app, db):
    await configure_profile(app.tg, db)
    commands = [p for method, p in app.tg.calls if method == "setMyCommands" and "language_code" not in p]
    descriptions = [p for method, p in app.tg.calls if method == "setMyDescription" and "language_code" not in p]
    assert commands[0]["commands"] == commands_for("en")
    assert t("en", "welcome") in descriptions[0]["description"]
    assert await db.setting("profile_version") == PROFILE_VERSION
    assert {
        p["language_code"] for method, p in app.tg.calls if method == "setMyCommands" and "language_code" in p
    } == set(LANGS)


async def test_upgrade_preserves_an_existing_language_choice(tmp_path):
    import sqlite3
    from astrobot.db import DB, SCHEMA

    path = tmp_path / "legacy-language.db"
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.execute("INSERT INTO users(id,name,lang,created,last_seen) VALUES(2,'Existing user','fa',0,0)")
    migrated = await DB().open(path)
    try:
        user = await migrated.user(2)
        assert user["lang"] == "fa" and user["language_selected"] == 1
        await migrated.touch(3, "New user")
        assert (await migrated.user(3))["language_selected"] == 0
    finally:
        await migrated.close()
