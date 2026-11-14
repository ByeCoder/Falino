"""Consistent SQLite online backup. Session and credentials need separate secure backups."""

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--data-dir", default="data")
p.add_argument("--output", default="backups")
args = p.parse_args()
source = Path(args.data_dir) / "astra.sqlite3"
if not source.is_file():
    raise SystemExit("Database does not exist")
folder = Path(args.output)
folder.mkdir(mode=0o700, parents=True, exist_ok=True)
target = folder / ("astra-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + ".sqlite3")
with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as src, sqlite3.connect(target) as dst:
    src.backup(dst)
target.chmod(0o600)
print(target)
