import asyncio
import time
from datetime import date, datetime, timezone

import httpx
import pytest
import pytest_asyncio

from astrobot.app import App
from astrobot.core import Config, next_delivery, parse_birth, sign_for, validate_clock
from astrobot.db import DB
from astrobot.i18n import TEXTS
from astrobot.scheduler import Scheduler
from astrobot.services import Horoscope, Membership, Telegram, TelegramError, Unavailable


@pytest.fixture
def config(tmp_path):
    return Config(123, "test-hash", "123:test-token", frozenset({1}), tmp_path)


@pytest_asyncio.fixture
async def db(tmp_path):
    db = await DB().open(tmp_path / "test.sqlite3")
    yield db
    await db.close()


class FakeTelegram:
    def __init__(self):
        self.messages = []
        self.status = "member"
        self.fail = False
        self.calls = []

    async def send(self, chat, text, keyboard=None):
        if self.fail:
            raise TelegramError(403, "blocked")
        self.messages.append((chat, text, keyboard))
        return {"message_id": len(self.messages)}

    async def call(self, method, **payload):
        self.calls.append((method, payload))
        if self.fail:
            raise Unavailable("network")
        if method == "getChatMember":
            return {"status": self.status, "is_member": self.status == "restricted", "can_post_messages": True}
        if method == "getChat":
            return {"id": -100123456789, "type": "channel", "title": "Test"}
        return {}


class FakeHoro:
    async def cards(self, sign, period, lang):
        return [f"{sign}:{period}:part1", f"{sign}:{period}:part2"]


@pytest_asyncio.fixture
async def app(config, db):
    tg = FakeTelegram()
    app = App(config, db, tg, FakeHoro(), Membership(db, tg, config.admins))
    app.bot_id = 99
    app.username = "AstraTestBot"
    return app


async def start(app, uid=2):
    """Register and explicitly select Persian for existing Persian-flow tests."""
    await app.dispatch(uid, "Tester", "fa", text="/start")
    app.clicks.clear()
    await app.dispatch(uid, "Tester", "fa", callback="lang:fa")
    app.clicks.clear()


@pytest.mark.parametrize(
    "birthday,expected",
    [
        ("2000-01-19", "capricorn"),
        ("2000-01-20", "aquarius"),
        ("2000-02-29", "pisces"),
        ("2000-03-20", "pisces"),
        ("2000-03-21", "aries"),
        ("2000-12-21", "sagittarius"),
        ("2000-12-22", "capricorn"),
    ],
)
def test_zodiac_boundaries(birthday, expected):
    assert sign_for(date.fromisoformat(birthday)) == expected


def test_jalali_and_persian_digits():
    assert parse_birth("۱۳۷۴/۰۱/۲۳", "j") == date(1995, 4, 12)
    with pytest.raises(ValueError):
        parse_birth("1402-12-30", "j")
    with pytest.raises(ValueError):
        parse_birth("2100-01-01", "g", today=date(2026, 1, 1))


def test_tehran_next_delivery():
    after = datetime(2026, 11, 14, 5, 0, tzinfo=timezone.utc)
    result = datetime.fromtimestamp(next_delivery("08:30", "Asia/Tehran", after), timezone.utc)
    assert result == datetime(2026, 11, 15, 5, 0, tzinfo=timezone.utc)
    assert validate_clock("۰۸:۳۰ Asia/Tehran") == ("08:30", "Asia/Tehran")
    with pytest.raises(Exception):
        validate_clock("25:00 Fake/Zone")


def test_locale_key_parity():
    assert all(set(v) == set(TEXTS["en"]) for v in TEXTS.values())


async def test_admin_authorization(app, db):
    await start(app)
    await app.dispatch(2, "Tester", "fa", text="/panel")
    before = await db.setting("theme")
    app.clicks.clear()
    await app.dispatch(2, "Tester", "fa", callback="admin:style:danger")
    assert await db.setting("theme") == before
    # Persisted admin state alone never grants privileges.
    await db.set_state(2, {"kind": "admin:footer"})
    await app.dispatch(2, "Tester", "fa", text="intrusion")
    assert await db.setting("footer") is None


async def test_membership_enforced_on_callbacks(app, db):
    await start(app)
    await db.set("required_channels", [{"id": -1001, "title": "Test", "url": "https://t.me/test1"}])
    app.tg.status = "left"
    app.clicks.clear()
    await app.dispatch(2, "Tester", "fa", callback="read:daily:aries")
    assert "بررسی عضویت" in str(app.tg.messages[-1])
    assert not any("aries:daily" in m[1] for m in app.tg.messages)
    app.tg.fail = True
    with pytest.raises(Unavailable):
        await app.membership.allowed(2)
    assert await app.membership.allowed(1)  # Admins can repair broken channels.


async def test_birth_flow_and_explicit_subscription(app, db):
    await start(app)
    await db.set_state(2, {"kind": "birth", "calendar": "j"})
    await app.dispatch(2, "Tester", "fa", text="۱۳۷۴/۰۱/۲۳")
    user = await db.user(2)
    assert user["birth"] == "1995-04-12" and user["sign"] == "aries"
    assert user["subscribed"] == 0
    await app.dispatch(2, "Tester", "fa", text="/daily")
    assert (await db.user(2))["subscribed"] == 1


async def test_delete_works_without_membership(app, db):
    await start(app)
    await db.set("required_channels", [{"id": -1001, "title": "Test", "url": "https://t.me/test1"}])
    app.tg.status = "left"
    await db.cache("natal:2:private", {"private": True})
    await app.dispatch(2, "Tester", "fa", text="/delete_me")
    app.clicks.clear()
    await app.dispatch(2, "Tester", "fa", callback="delete:yes")
    assert await db.user(2) is None
    assert await db.cached("natal:2:private") is None
    app.clicks.clear()
    await app.dispatch(2, "Tester", "fa", callback="home")
    assert await db.user(2) is None


async def test_personal_delivery_survives_scheduler_restart(app, db):
    await start(app)
    await db.execute("UPDATE users SET sign='aries',subscribed=1,next_due=0 WHERE id=2")
    app.tg.messages.clear()
    await Scheduler(app).personal()
    assert len(app.tg.messages) == 2
    await db.execute("UPDATE users SET next_due=0 WHERE id=2")
    await Scheduler(app).personal()
    assert len(app.tg.messages) == 2


async def test_partial_channel_delivery_retries_only_unsent_parts(app, db):
    import astrobot.scheduler as mod

    original = mod.channel_cards

    async def payload(app, job):
        return ["one", "two", "three"]

    mod.channel_cards = payload
    try:
        due = time.time() - 2
        jid = await db.execute(
            "INSERT INTO jobs(chat_id,title,hours,kind,lang,sign,next_due) VALUES(-1001,'Test',6,'daily','fa','aries',?)",
            (due,),
        )
        await db.mark(f"job:{jid}", str(due), 0)
        await Scheduler(app).channels()
        assert [m[1] for m in app.tg.messages] == ["two", "three"]
        row = await db.one("SELECT * FROM jobs WHERE id=?", (jid,))
        assert row["next_due"] > time.time()
    finally:
        mod.channel_cards = original


async def test_blocked_subscriber_is_disabled(app, db):
    await start(app)
    await db.execute("UPDATE users SET sign='aries',subscribed=1,next_due=0 WHERE id=2")
    app.tg.fail = True
    await Scheduler(app).personal()
    user = await db.user(2)
    assert user["blocked"] == 1 and user["subscribed"] == 0


async def test_provider_cache_coalesces_concurrent_calls(config, db):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(
            200, json={"data": {"sign": "Aries", "period": "daily", "date": "2026-11-14", "horoscope": "A calm day."}}
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    service = Horoscope(db, config, client)
    try:
        results = await asyncio.gather(*(service.reading("aries", "daily") for _ in range(12)))
        assert len(calls) == 1 and len(results) == 12
    finally:
        await service.close()


async def test_invalid_provider_response_not_cached(config, db):
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                200, json={"data": {"sign": "Pisces", "period": "daily", "date": "bad", "horoscope": "x"}}
            )
        )
    )
    service = Horoscope(db, config, client)
    try:
        with pytest.raises(Unavailable):
            await service.reading("aries", "daily")
        assert await db.all("SELECT * FROM cache") == []
    finally:
        await service.close()


async def test_long_reading_html_is_safe(config, db):
    text = '&<>"😀' * 2000
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                200, json={"data": {"sign": "Aries", "period": "daily", "date": "2026-11-13", "horoscope": text}}
            )
        )
    )
    service = Horoscope(db, config, client)
    try:
        cards = await service.cards("aries", "daily", "fa")
        assert len(cards) > 1
        assert all(len(c) < 4096 for c in cards)
        assert all("<>" not in c for c in cards)
        assert any("تاریخ منبع" in c and "2026-11-13" in c for c in cards)
    finally:
        await service.close()


async def test_premium_decorations_fall_back(config):
    bodies = []

    def respond(request):
        import json

        data = json.loads(request.content)
        bodies.append(data)
        if len(bodies) == 1:
            return httpx.Response(
                400, json={"ok": False, "error_code": 400, "description": "Bad Request: custom emoji not allowed"}
            )
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    tg = Telegram(config, httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    try:
        await tg.send(
            2,
            '<tg-emoji emoji-id="123">✨</tg-emoji> Hello',
            [[{"text": "Today", "callback_data": "p:daily", "style": "primary", "icon_custom_emoji_id": "123"}]],
        )
        assert len(bodies) == 2
        assert "tg-emoji" not in bodies[1]["text"]
        assert "icon_custom_emoji_id" not in bodies[1]["reply_markup"]["inline_keyboard"][0][0]
    finally:
        await tg.close()


async def test_broadcast_requires_admin_confirmation(app, db):
    await start(app, 1)
    await start(app, 2)
    await db.set_state(1, {"kind": "admin:broadcast"})
    await app.dispatch(1, "Owner", "fa", text="A public announcement")
    assert await db.all("SELECT * FROM broadcasts") == []
    app.clicks.clear()
    await app.dispatch(1, "Owner", "fa", callback="admin:bconfirm")
    assert len(await db.all("SELECT * FROM broadcasts")) == 1
    await Scheduler(app).broadcasts()
    assert len([m for m in app.tg.messages if m[1] == "A public announcement"]) == 2


async def test_referral_does_not_overwrite_existing_user(app, db):
    await start(app, 1)
    await app.dispatch(2, "User", "fa", text="/start ref_1")
    assert (await db.user(2))["referred_by"] == 1
    await app.dispatch(2, "User", "fa", text="/start ref_999")
    assert (await db.user(2))["referred_by"] == 1


async def test_membership_403_does_not_disable_subscription(app, db):
    await start(app)
    await db.execute("UPDATE users SET sign='aries',subscribed=1,next_due=0 WHERE id=2")
    await db.set("required_channels", [{"id": -1001, "title": "Test", "url": "https://t.me/test1"}])

    async def kicked(method, **payload):
        raise TelegramError(403, "bot was kicked from channel")

    app.tg.call = kicked
    await Scheduler(app).personal()
    user = await db.user(2)
    assert user["blocked"] == 0 and user["subscribed"] == 1
    assert user["next_due"] > time.time()


async def test_manual_view_suppresses_daily_auto_delivery(app, db):
    await start(app)
    await db.execute("UPDATE users SET sign='aries',subscribed=1,next_due=0 WHERE id=2")
    await app.dispatch(2, "Tester", "fa", text="/today")
    app.tg.messages.clear()
    await Scheduler(app).personal()
    assert app.tg.messages == []


async def test_annual_is_editor_content_not_a_fake_endpoint(config, db):
    await db.execute(
        "INSERT INTO annual VALUES(?,?,?,?)", (datetime.now(timezone.utc).year, "aries", "fa", "متن سالانه مدیر")
    )

    def no_requests(request):
        raise AssertionError("Yearly endpoint must never be called")

    service = Horoscope(db, config, httpx.AsyncClient(transport=httpx.MockTransport(no_requests)))
    try:
        cards = await service.cards("aries", "yearly", "fa")
        assert "متن سالانه مدیر" in cards[0]
        assert "مدیر ربات" in cards[0]
        missing = await service.cards("pisces", "yearly", "fa")
        assert "هنوز" in missing[0]
    finally:
        await service.close()


async def test_one_endpoint_outage_does_not_disable_other_endpoints(config, db, monkeypatch):
    import astrobot.services as mod

    async def no_wait(*args):
        pass

    monkeypatch.setattr(mod.asyncio, "sleep", no_wait)

    def response(request):
        if "/weekly" in request.url.path:
            return httpx.Response(504, json={"error": "upstream timeout"})
        return httpx.Response(
            200, json={"data": {"sign": "Aries", "period": "daily", "date": "2026-11-14", "horoscope": "OK"}}
        )

    service = Horoscope(db, config, httpx.AsyncClient(transport=httpx.MockTransport(response)))
    try:
        with pytest.raises(Unavailable):
            await service.reading("aries", "weekly")
        assert (await service.reading("aries", "daily"))["horoscope"] == "OK"
    finally:
        await service.close()
