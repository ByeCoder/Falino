"""Local SQLite/handler benchmark; no Telegram or provider network calls.

This is not a production throughput guarantee: external API, Telegram rate limits,
translations and audit-group delivery are intentionally excluded.
"""

import argparse
import asyncio
import resource
import tempfile
import time
from pathlib import Path

from astrobot.app import App
from astrobot.core import Config
from astrobot.db import DB
from astrobot.services import Membership


class LocalTelegram:
    async def send(self, chat, text, keyboard=None):
        return {"message_id": 1}

    async def call(self, method, **kwargs):
        return {"status": "member"}


class LocalReadings:
    async def cards(self, sign, period, lang):
        return ["<b>Local benchmark reading</b>\nA short example."]


async def run(count):
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        db = await DB().open(root / "bench.db")
        cfg = Config(0, "", "", frozenset({1}), root)
        tg = LocalTelegram()
        app = App(cfg, db, tg, LocalReadings(), Membership(db, tg, cfg.admins))
        app.username = "benchmark"
        start = time.perf_counter()
        try:
            for i in range(2, count + 2):
                await app.dispatch(i, "Benchmark user", "fa", text="/start")
                await db.execute("UPDATE users SET sign='aries' WHERE id=?", (i,))
                await app.show(i, "aries", "daily", "fa")
            seconds = time.perf_counter() - start
            size = sum(p.stat().st_size for p in root.iterdir() if p.is_file())
            print(f"Profiles + daily readings: {count}")
            print(f"Elapsed: {seconds:.2f}s")
            print(f"Peak RSS (Linux): {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.1f} MiB")
            print(f"Database + WAL + SHM: {size / 1024 / 1024:.2f} MiB")
            print("Local handlers/SQLite only. Network, translations and log delivery excluded.")
        finally:
            await db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=1000)
    args = parser.parse_args()
    if not 1 <= args.users <= 100000:
        parser.error("--users must be 1..100000")
    asyncio.run(run(args.users))
