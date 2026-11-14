"""Live provider check. No Telegram credentials or messages are used."""

import asyncio
import tempfile
from pathlib import Path

from astrobot.core import Config
from astrobot.db import DB
from astrobot.services import Horoscope, Unavailable


async def main():
    failures = 0
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        db = await DB().open(root / "smoke.db")
        service = Horoscope(db, Config(0, "", "", frozenset(), root))
        try:
            for period in ("daily", "weekly", "monthly"):
                try:
                    row = await service.reading("aries", period)
                    print(f"{period}: OK | provider date={row['date']} | chars={len(row['horoscope'])}", flush=True)
                except Unavailable:
                    failures += 1
                    print(f"{period}: UNAVAILABLE (provider or network)", flush=True)
            try:
                cards = await service.tarot("en", "smoke-test")
                print(f"tarot: OK | messages={len(cards)}", flush=True)
            except Unavailable:
                failures += 1
                print("tarot: UNAVAILABLE", flush=True)
            try:
                spread = await service.spread(0, "en")
                print(f"three-card-tarot: OK | messages={len(spread)}", flush=True)
            except Unavailable:
                failures += 1
                print("three-card-tarot: UNAVAILABLE", flush=True)
            try:
                natal = await service.natal(0, "1995-04-12", "14:30", "Asia/Tehran", "en")
                print(f"planetary-positions: OK | chars={len(natal)}", flush=True)
            except Unavailable:
                failures += 1
                print("planetary-positions: UNAVAILABLE", flush=True)
        finally:
            await service.close()
            await db.close()
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
