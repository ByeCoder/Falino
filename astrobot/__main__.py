from __future__ import annotations

import asyncio
import contextlib
import fcntl
import logging
import os
import signal

from telethon import TelegramClient, events
from python_socks import parse_proxy_url

from .app import App
from .core import Config, FALLBACK_LANGUAGE
from .db import DB
from .i18n import t
from .metadata import configure_profile
from .scheduler import Scheduler
from .services import Horoscope, Membership, Telegram, TelegramError, Unavailable

log = logging.getLogger("astra")


async def main():
    cfg = Config.load()
    cfg.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(cfg.data_dir, 0o700)
    # SQLite + one worker process. A shared data volume cannot run two instances.
    lock = (cfg.data_dir / "bot.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("Another bot instance is using this DATA_DIR") from None
    db = await DB().open(cfg.data_dir / "astra.sqlite3")
    tg = Telegram(cfg)
    horo = Horoscope(db, cfg)
    membership = Membership(db, tg, cfg.admins)
    app = App(cfg, db, tg, horo, membership)
    proxy = None
    if cfg.mtproxy:
        protocol, host, port, username, password = parse_proxy_url(cfg.mtproxy)
        proxy = {
            "proxy_type": protocol,
            "addr": host,
            "port": port,
            "username": username,
            "password": password,
            "rdns": True,
        }
    client = TelegramClient(
        str(cfg.data_dir / "bot"),
        cfg.api_id,
        cfg.api_hash,
        proxy=proxy,
        auto_reconnect=True,
        connection_retries=10,
        request_retries=3,
        flood_sleep_threshold=60,
        receive_updates=True,
        entity_cache_limit=1000,
    )
    scheduler = Scheduler(app)

    active_users = set()

    async def handle(uid, name, language, text="", callback=None, identity=None, context=None):
        # Bound work and avoid accumulating queued handlers under message floods.
        if uid in active_users or len(active_users) >= 64:
            return
        active_users.add(uid)
        try:
            await app.dispatch(uid, name, language, text, callback, identity, context)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("Interaction failed (%s)", type(exc).__name__)
            with contextlib.suppress(Exception):
                await app.extra.analytics.record(
                    uid,
                    "error",
                    type(exc).__name__,
                    source=(
                        callback.split(":")[0]
                        if callback
                        else text.split(maxsplit=1)[0]
                        if text.startswith("/")
                        else "input"
                    )[:40],
                )
            with contextlib.suppress(Exception):
                user = await db.user(uid)
                await app.send(uid, t(user["lang"] if user else FALLBACK_LANGUAGE, "error"))
        finally:
            active_users.discard(uid)

    def identity_of(sender):
        return {
            "last_name": getattr(sender, "last_name", "") or "",
            "username": getattr(sender, "username", "") or "",
            "premium": bool(getattr(sender, "premium", False)),
            "telegram_lang": getattr(sender, "lang_code", "") or "",
        }

    @client.on(events.NewMessage(incoming=True))
    async def message(event):
        if not event.sender_id or event.sender_id <= 0:
            return
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return
        context = {"message_id": event.id, "chat_id": event.chat_id, "media": bool(event.photo or event.document)}
        if event.sender_id in cfg.admins:
            try:
                handled = await app.extra.support.staff_message(
                    event.sender_id,
                    event.chat_id,
                    event.raw_text,
                    getattr(event.message, "reply_to_msg_id", None),
                    context,
                )
                if handled:
                    return
            except Exception as exc:
                log.warning("Staff interaction failed (%s)", type(exc).__name__)
                return
        if not event.is_private:
            return
        await handle(
            event.sender_id,
            getattr(sender, "first_name", "") or "User",
            getattr(sender, "lang_code", FALLBACK_LANGUAGE) or FALLBACK_LANGUAGE,
            text=event.raw_text,
            identity=identity_of(sender),
            context=context,
        )

    @client.on(events.CallbackQuery())
    async def callback(event):
        if not event.is_private or not event.sender_id or event.sender_id <= 0:
            return
        # Answer immediately; API work and translation may take several seconds.
        with contextlib.suppress(Exception):
            await event.answer()
        sender = await event.get_sender()
        try:
            data = event.data.decode("utf-8")
        except (UnicodeError, AttributeError):
            return
        await handle(
            event.sender_id,
            getattr(sender, "first_name", "") or "User",
            getattr(sender, "lang_code", FALLBACK_LANGUAGE) or FALLBACK_LANGUAGE,
            callback=data,
            identity=identity_of(sender),
        )

    try:
        # Bot API webhooks are unnecessary: inbound events use Telethon exclusively.
        await tg.call("deleteWebhook", drop_pending_updates=False)
        await client.start(bot_token=cfg.token)
        me = await client.get_me()
        app.bot_id, app.username = me.id, me.username
        http_me = await tg.call("getMe")
        if http_me["id"] != me.id:
            raise RuntimeError("Session belongs to another bot; use a new DATA_DIR")
        # Profile descriptions and command defaults are English; localized lists
        # stay available for all ten supported Telegram locales.
        with contextlib.suppress(TelegramError, Unavailable):
            await configure_profile(tg, db)
        scheduler.start()
        loop = asyncio.get_running_loop()
        stop = asyncio.Event()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
        log.info("Falino started as @%s", app.username)
        stopped = asyncio.create_task(stop.wait())
        disconnected = asyncio.ensure_future(client.disconnected)
        await asyncio.wait([stopped, disconnected], return_when=asyncio.FIRST_COMPLETED)
        stopped.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stopped
    finally:
        await scheduler.stop()
        await client.disconnect()
        await horo.close()
        await tg.close()
        await db.close()
        lock.close()


if __name__ == "__main__":
    os.umask(0o077)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for name in ("httpx", "httpcore", "telethon"):
        logging.getLogger(name).setLevel(logging.WARNING)
    try:
        asyncio.run(main())
    except (ValueError, Unavailable, TelegramError) as exc:
        # Config errors are safe; transport exception strings can include secret URLs.
        print(str(exc) if isinstance(exc, ValueError) else "Startup failed: verify credentials and network access.")
        raise SystemExit(1) from None
