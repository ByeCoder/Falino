import json
import sqlite3
import time
from datetime import datetime, timezone

import httpx
import pytest

from astrobot.analytics import calendar_windows
from astrobot.core import LANGS, SIGN_NAMES, normalize_language
from astrobot.db import DB
from astrobot.i18n import TEXTS
from astrobot.scheduler import Scheduler, is_birthday
from astrobot.services import Horoscope, Unavailable

# Reuse the original fixtures without copying their implementation.
from test_bot import start


def test_requested_languages_and_order():
    assert list(LANGS)[:2] == ["zh", "hi"]
    assert set(LANGS) == {"zh", "hi", "fa", "ar", "en", "ru", "he", "es", "fr", "tr"}
    assert set(TEXTS) == set(LANGS)
    assert all(set(v) == set(TEXTS["en"]) for v in TEXTS.values())
    assert all(len(SIGN_NAMES[lang]) == 12 for lang in LANGS)
    assert normalize_language("zh-hans") == "zh"
    assert normalize_language("hi-IN") == "hi"
    assert normalize_language("iw") == "he"
    assert normalize_language("ar-SA") == "ar"
    for lang, values in TEXTS.items():
        assert "{id}" in values["support_sent"]
        assert "{name}" in values["birthday_text"]
        assert values["support_sent"].format(id=123)


def test_calendar_statistics_are_tehran_saturday_and_jalali():
    windows = calendar_windows(datetime(2026, 11, 14, 12, tzinfo=timezone.utc))
    assert windows["daily"] == "2026-11-14"
    assert windows["weekly"] == "2026-11-14"
    assert windows["monthly"] == "2026-10-23"
    # Before midnight UTC can already be the next day in Tehran.
    assert calendar_windows(datetime(2026, 11, 14, 22, tzinfo=timezone.utc))["daily"] == "2026-11-15"


async def test_upgrade_preserves_legacy_users_and_is_idempotent(tmp_path):
    path = tmp_path / "legacy.db"
    import astrobot.db as mod

    with sqlite3.connect(path) as conn:
        conn.executescript(mod.SCHEMA)
        conn.execute(
            "INSERT INTO users(id,name,created,last_seen) VALUES(2,'Old user',?,?)", (time.time() - 86400, time.time())
        )
    first = await DB().open(path)
    assert (await first.user(2))["name"] == "Old user"
    assert (await first.user(2))["points"] == 0
    count = await first.one("SELECT SUM(count) n FROM metric_days WHERE kind='register'")
    assert count["n"] == 1
    await first.close()
    second = await DB().open(path)
    assert (await second.one("SELECT SUM(count) n FROM metric_days WHERE kind='register'"))["n"] == 1
    await second.close()


async def test_daily_stats_count_unique_active_and_successful_readings(app, db):
    await start(app)
    await app.dispatch(2, "Tester", "fa", text="/menu")
    await db.execute("UPDATE users SET sign='aries' WHERE id=2")
    await app.dispatch(2, "Tester", "fa", text="/today")
    rows = await db.all("SELECT kind,SUM(count) n FROM metric_days GROUP BY kind")
    totals = {r["kind"]: r["n"] for r in rows}
    assert totals["register"] == 1 and totals["reading"] == 1
    assert (await db.one("SELECT COUNT(DISTINCT user_id) n FROM active_days"))["n"] == 1
    for period in ("daily", "weekly", "monthly", "all"):
        report = await app.extra.analytics.report(period)
        assert "دریافت موفق فال: 1" in report
        assert "کاربر فعال یکتا: 1" in report


async def test_stats_periods_filter_old_readings(app, db):
    await start(app)
    await db.execute("INSERT INTO metric_days VALUES('2020-01-01','reading','daily',99)")
    assert "دریافت موفق فال: 0" in await app.extra.analytics.report("daily")
    assert "دریافت موفق فال: 99" in await app.extra.analytics.report("all")


async def test_failed_send_is_not_counted_as_received(app, db):
    await start(app)
    await db.execute("UPDATE users SET sign='aries' WHERE id=2")
    app.tg.fail = True
    with pytest.raises(Exception):
        await app.show(2, "aries", "daily", "fa")
    assert (await db.one("SELECT COUNT(*) n FROM events WHERE kind='reading'"))["n"] == 0
    assert (await db.one("SELECT COUNT(*) n FROM history WHERE delivered=1"))["n"] == 0


async def test_support_two_way_reply_and_authorization(app, db):
    await start(app)
    await app.dispatch(2, "Tester", "fa", text="/support")
    await app.dispatch(2, "Tester", "fa", text="سلام، کمک می‌خواهم")
    ticket = await db.one("SELECT * FROM tickets WHERE user_id=2")
    assert ticket["status"] == "open"
    await app.extra.support.drain()
    route = await db.one("SELECT * FROM staff_routes LIMIT 1")
    assert route and route["chat_id"] == 1
    before = len(app.tg.messages)
    assert not await app.extra.support.staff_message(999, 1, "intrusion", route["message_id"])
    assert len(app.tg.messages) == before
    assert await app.extra.support.staff_message(1, 1, "سلام، کنارت هستیم", route["message_id"])
    assert any(m[0] == 2 and "کنارت هستیم" in m[1] for m in app.tg.messages)
    reply = await db.one("SELECT * FROM ticket_messages WHERE role='staff'")
    assert reply["ticket_id"] == ticket["id"]


async def test_private_support_is_available_behind_membership_wall(app, db):
    await start(app)
    await db.set("required_channels", [{"id": -1001, "title": "Test", "url": "https://t.me/test1"}])
    app.tg.status = "left"
    await app.dispatch(2, "Tester", "fa", text="/support")
    await app.dispatch(2, "Tester", "fa", text="عضویت من مشکل دارد")
    assert await db.one("SELECT id FROM tickets WHERE user_id=2")


async def test_ticket_close_and_owner_checks(app, db):
    await start(app)
    await start(app, 3)
    await app.extra.support.submit(2, "Question")
    tid = (await db.one("SELECT id FROM tickets"))["id"]
    assert not await app.extra.support.close(3, tid)
    assert await app.extra.support.close(2, tid)
    assert not await app.extra.support.reply(1, tid, "late reply")
    assert not await app.extra.support.reply(3, tid, "unauthorized")


async def test_support_media_copied_without_download(app, db):
    await start(app)
    await app.extra.support.submit(2, "", {"media": True, "message_id": 123})
    await app.extra.support.drain()
    copies = [call for call in app.tg.calls if call[0] == "copyMessage"]
    assert copies and copies[0][1]["from_chat_id"] == 2 and copies[0][1]["message_id"] == 123


async def test_internal_support_note_never_sent_to_user(app, db):
    await start(app)
    await app.extra.support.submit(2, "Question")
    await app.extra.support.drain()
    route = await db.one("SELECT * FROM staff_routes LIMIT 1")
    app.tg.messages.clear()
    await app.extra.support.staff_message(1, 1, "!note secret staff note", route["message_id"])
    assert not any(m[0] == 2 for m in app.tg.messages)
    assert await db.one("SELECT 1 FROM ticket_messages WHERE role='internal'")


async def test_support_rate_limit_does_not_create_extra_messages(app, db):
    await start(app)
    for _ in range(11):
        await app.extra.support.submit(2, "Question")
    assert (await db.one("SELECT COUNT(*) n FROM ticket_messages WHERE role='user'"))["n"] == 10


async def test_full_profile_and_reading_type_go_to_log_queue(app, db):
    await start(app)
    await db.set("log_group", -10099)
    await db.touch(
        2,
        "Pouya",
        "fa",
        identity={"last_name": "<Admin>", "username": "example", "telegram_lang": "fa", "premium": True},
    )
    await db.execute("UPDATE users SET birth='1995-04-12',sign='aries' WHERE id=2")
    await app.show(2, "aries", "daily", "fa")
    queued = await db.one("SELECT * FROM outbox WHERE kind='audit'")
    payload = json.loads(queued["payload"])
    assert "روزانه" in payload["text"] and "aries" in payload["text"]
    assert "1995-04-12" in payload["text"] and "@example" in payload["text"]
    assert "&lt;Admin&gt;" in payload["text"] and "<Admin>" not in payload["text"]
    await Scheduler(app).outbox()
    assert await db.one("SELECT * FROM log_messages WHERE user_id=2")


async def test_delete_cascades_private_history_tickets_and_queued_logs(app, db):
    await start(app)
    await db.set("log_group", -10099)
    await app.show(2, "aries", "daily", "fa")
    await app.extra.support.submit(2, "Private question")
    await db.execute("INSERT INTO log_messages VALUES(2,-10099,123,?)", (time.time(),))
    await db.forget(2)
    assert await db.user(2) is None
    for table in ("history", "tickets", "active_days", "outbox"):
        if table == "outbox":
            assert not await db.one("SELECT 1 FROM outbox WHERE user_id=2")
        else:
            assert not await db.one(f"SELECT 1 FROM {table} WHERE user_id=2")
    assert await db.one("SELECT * FROM outbox WHERE kind='delete' AND user_id IS NULL")
    assert not await db.one("SELECT 1 FROM events WHERE user_id=2")


async def test_history_and_favorites_are_owner_only(app, db):
    await start(app)
    await start(app, 3)
    await app.show(2, "aries", "daily", "fa")
    hid = (await db.one("SELECT id FROM history"))["id"]
    app.tg.messages.clear()
    await app.extra.route(3, await db.user(3), "", f"hview:{hid}")
    assert not any("aries:daily" in m[1] for m in app.tg.messages)
    await app.extra.route(3, await db.user(3), "", f"hfav:{hid}")
    assert (await db.one("SELECT favorite FROM history WHERE id=?", (hid,)))["favorite"] == 0
    await app.extra.route(2, await db.user(2), "", f"hfav:{hid}")
    assert (await db.one("SELECT favorite FROM history WHERE id=?", (hid,)))["favorite"] == 1


async def test_daily_and_quest_rewards_cannot_be_farmed(app, db):
    await start(app)
    await app.extra.claim(2, "daily")
    await app.extra.claim(2, "daily")
    assert (await db.user(2))["points"] == 5
    # A daily quest needs BOTH a daily reading and today's mood.
    await app.extra.claim(2, "quest")
    assert (await db.user(2))["points"] == 5
    await app.show(2, "aries", "daily", "fa")
    from zoneinfo import ZoneInfo
    from astrobot.core import now_utc

    day = now_utc().astimezone(ZoneInfo("Asia/Tehran")).date().isoformat()
    await db.execute("INSERT INTO moods VALUES(?,?,?)", (2, day, 8))
    await app.extra.claim(2, "quest")
    await app.extra.claim(2, "quest")
    assert (await db.user(2))["points"] == 15


async def test_referral_reward_only_after_completed_profile_and_once(app, db):
    await start(app, 1)
    await app.dispatch(2, "User", "fa", text="/start ref_1")
    await app.show(2, "aries", "daily", "fa")
    assert (await db.user(1))["points"] == 0
    await db.execute("UPDATE users SET birth='1995-04-12' WHERE id=2")
    await app.show(2, "aries", "daily", "fa")
    await app.show(2, "aries", "daily", "fa")
    assert (await db.user(1))["points"] == 30
    assert (await db.user(2))["ref_rewarded"] == 1


async def test_history_retention_bounded_but_favorites_preserved(app, db):
    await start(app)
    first = None
    for i in range(35):
        hid = await app.extra.save_history(2, "daily", "aries", "fa", ["card"])
        await db.execute("UPDATE history SET delivered=1 WHERE id=?", (hid,))
        if i == 0:
            first = hid
            await db.execute("UPDATE history SET favorite=1 WHERE id=?", (hid,))
    await app.extra.completed(2, "daily", "aries")
    assert (await db.one("SELECT COUNT(*) n FROM history WHERE user_id=2"))["n"] <= 31
    assert await db.one("SELECT 1 FROM history WHERE id=?", (first,))


async def test_goal_total_member_count_auto_disables_rule(app, db):
    await start(app)
    await db.set(
        "required_channels",
        [
            {
                "id": -1001,
                "title": "Test",
                "url": "https://t.me/test1",
                "goal": 100,
                "goal_mode": "members",
                "epoch": "a",
            }
        ],
    )

    async def call(method, **payload):
        if method == "getChatMemberCount":
            return 100
        raise AssertionError("No member lookup after goal reached")

    app.tg.call = call
    assert await app.membership.allowed(2)
    assert await app.membership.active_channels() == []
    assert (await db.one("SELECT complete FROM goal_progress"))["complete"] == 1


async def test_new_join_goal_excludes_existing_members_and_duplicates(app, db):
    await start(app)
    await start(app, 3)
    await db.set(
        "required_channels",
        [{"id": -1001, "title": "Test", "url": "https://t.me/test1", "goal": 2, "goal_mode": "joins", "epoch": "a"}],
    )
    app.tg.status = "member"
    assert await app.membership.allowed(2)
    assert (await db.one("SELECT count FROM goal_progress"))["count"] == 0
    app.tg.status = "left"
    assert not await app.membership.allowed(3)
    app.tg.status = "member"
    assert await app.membership.allowed(3)
    assert await app.membership.allowed(3)
    assert (await db.one("SELECT count FROM goal_progress"))["count"] == 1


async def test_goal_counter_failure_keeps_membership_required(app, db):
    await start(app)
    await db.set(
        "required_channels",
        [
            {
                "id": -1001,
                "title": "Test",
                "url": "https://t.me/test1",
                "goal": 100,
                "goal_mode": "members",
                "epoch": "a",
            }
        ],
    )

    async def call(method, **payload):
        if method == "getChatMemberCount":
            raise Unavailable("network")
        return {"status": "left"}

    app.tg.call = call
    assert not await app.membership.allowed(2)
    assert len(await app.membership.active_channels()) == 1


async def test_goal_join_attribution_checks_all_channels(app, db):
    await start(app)
    await db.set(
        "required_channels",
        [
            {"id": i, "title": "Test", "url": "https://t.me/test1", "goal": 5, "goal_mode": "joins", "epoch": "a"}
            for i in (-1001, -1002)
        ],
    )
    app.tg.status = "left"
    assert not await app.membership.allowed(2)
    assert (await db.one("SELECT COUNT(*) n FROM join_markers"))["n"] == 2


async def test_banned_user_cannot_get_reading_but_can_contact_support(app, db):
    await start(app)
    await db.execute("UPDATE users SET banned=1,sign='aries' WHERE id=2")
    await app.dispatch(2, "Tester", "fa", text="/today")
    assert not await db.one("SELECT 1 FROM events WHERE kind='reading'")
    await app.dispatch(2, "Tester", "fa", text="/support")
    await app.dispatch(2, "Tester", "fa", text="Please review my account")
    assert await db.one("SELECT 1 FROM tickets WHERE user_id=2")


async def test_saved_partner_deletion_is_owner_only(app, db):
    await start(app)
    await start(app, 3)
    await db.set_state(2, {"kind": "x:partner"})
    await app.extra.input(2, await db.user(2), "Sara / aries", {"kind": "x:partner"})
    partner = await db.one("SELECT * FROM partners")
    await app.extra.route(3, await db.user(3), "", f"pdelete:{partner['id']}")
    assert await db.one("SELECT 1 FROM partners WHERE id=?", (partner["id"],))


async def test_outbox_worker_registered_and_stops_cleanly(app):
    scheduler = Scheduler(app)
    scheduler.start()
    assert "outbox" in [task.get_name() for task in scheduler.tasks]
    await scheduler.stop()
    assert all(task.done() for task in scheduler.tasks)


async def test_birthday_calendar_and_leap_day():
    u = {"birth": "2000-02-29", "zone": "Asia/Tehran", "birth_calendar": "g"}
    assert is_birthday(u, datetime(2026, 2, 28, 12, tzinfo=timezone.utc))
    u = {"birth": "1995-04-12", "zone": "Asia/Tehran", "birth_calendar": "j"}
    assert is_birthday(u, datetime(2026, 4, 12, 12, tzinfo=timezone.utc))


async def test_spread_uses_three_distinct_provider_cards(config, db):
    calls = []

    def response(request):
        calls.append(request)
        cards = [{"name": f"Card {i}", "name_short": f"c{i}", "meaning_up": f"Meaning {i}"} for i in range(3)]
        return httpx.Response(200, json={"nhits": 3, "cards": cards})

    service = Horoscope(db, config, httpx.AsyncClient(transport=httpx.MockTransport(response)))
    try:
        assert len(await service.spread(2, "en")) == 4
        await service.spread(2, "en")
        assert len(calls) == 1
        assert calls[0].url.params["n"] == "3"
    finally:
        await service.close()


async def test_referral_cannot_be_repeated_by_deleting_and_recreating_profile(app, db):
    await start(app, 1)
    await app.dispatch(2, "User", "fa", text="/start ref_1")
    await db.execute("UPDATE users SET birth='1995-04-12' WHERE id=2")
    await app.show(2, "aries", "daily", "fa")
    await db.forget(2)
    await app.dispatch(2, "User", "fa", text="/start ref_1")
    await db.execute("UPDATE users SET birth='1995-04-12' WHERE id=2")
    await app.show(2, "aries", "daily", "fa")
    assert (await db.user(1))["points"] == 30


async def test_new_join_cannot_be_recounted_after_profile_deletion(app, db):
    await start(app)
    await db.set(
        "required_channels",
        [{"id": -1001, "title": "Test", "url": "https://t.me/test1", "goal": 5, "goal_mode": "joins", "epoch": "a"}],
    )
    app.tg.status = "left"
    assert not await app.membership.allowed(2)
    app.tg.status = "member"
    assert await app.membership.allowed(2)
    await db.forget(2)
    await db.touch(2, "Tester")
    app.tg.status = "left"
    assert not await app.membership.allowed(2)
    app.tg.status = "member"
    assert await app.membership.allowed(2)
    assert (await db.one("SELECT count FROM goal_progress"))["count"] == 1


async def test_new_locale_menus_fit_telegram_limits(app, db):
    await start(app)
    for lang in LANGS:
        app.tg.messages.clear()
        await db.execute("UPDATE users SET lang=? WHERE id=2", (lang,))
        await app.menu(2, lang)
        await app.extra.route(2, await db.user(2), "", "explore")
        await app.extra.public_route(2, await db.user(2), "/privacy", None)
        for _, text, rows in app.tg.messages:
            assert len(text) <= 4096
            for row in rows or []:
                for button in row:
                    assert 1 <= len(button["text"]) <= 64
                    if "callback_data" in button:
                        assert len(button["callback_data"].encode()) <= 64


async def test_panel_reply_state_accepts_attachments(app, db):
    await start(app, 1)
    await start(app, 2)
    await app.extra.support.submit(2, "Please send a file")
    tid = (await db.one("SELECT id FROM tickets"))["id"]
    await db.set_state(1, {"kind": "admin:reply", "ticket": tid})
    await app.dispatch(1, "Admin", "fa", text="", context={"media": True, "message_id": 321, "chat_id": 1})
    copies = [p for method, p in app.tg.calls if method == "copyMessage"]
    assert copies[-1]["chat_id"] == 2 and copies[-1]["message_id"] == 321
    assert await db.state(1) is None


async def test_history_and_admin_job_lists_are_paginated(app, db):
    await start(app)
    for _ in range(18):
        hid = await app.extra.save_history(2, "daily", "aries", "fa", ["card"])
        await db.execute("UPDATE history SET delivered=1 WHERE id=?", (hid,))
    await app.extra.history(2, "fa")
    assert "hpage:1:0" in str(app.tg.messages[-1][2])
    await app.extra.history(2, "fa", page=1)
    assert "hpage:0:0" in str(app.tg.messages[-1][2])
    for i in range(21):
        await db.execute(
            "INSERT INTO jobs(chat_id,title,hours,kind,lang,sign,next_due) VALUES(-1001,?,24,'daily','fa','aries',?)",
            (f"Job{i}", time.time() + 86400),
        )
    await app.admin(1, "admin:jobs")
    assert "admin:jobs:1" in str(app.tg.messages[-1][2])
    await app.admin(1, "admin:jobs:1")
    assert "admin:jobs:0" in str(app.tg.messages[-1][2])


async def test_banned_accounts_do_not_starve_due_delivery_batch(app, db):
    for uid in range(2, 102):
        await db.touch(uid, "Banned")
        await db.execute("UPDATE users SET banned=1,subscribed=1,sign='aries',next_due=0 WHERE id=?", (uid,))
    await start(app, 1000)
    await db.execute("UPDATE users SET subscribed=1,sign='aries',next_due=1 WHERE id=1000")
    app.tg.messages.clear()
    await Scheduler(app).personal()
    assert len(app.tg.messages) == 2
    assert all(m[0] == 1000 for m in app.tg.messages)
