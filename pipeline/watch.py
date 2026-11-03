"""The loop: fetch every configured source, diff against the store, log changes."""

import argparse
import csv
import json
import os
import time

from . import sources
from .store import Store


def run(config_path: str, db_path: str):
    with open(config_path) as f:
        cfg = json.load(f)

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    store = Store(db_path)

    for name, url in cfg.get("sources", {}).items():
        rows = sources.fetch(url)
        changed = store.upsert(name, rows)
        if changed:
            with open("changes.csv", "a", newline="") as f:
                w = csv.writer(f)
                for r in changed:
                    w.writerow([
                        time.strftime("%Y-%m-%d %H:%M"),
                        name, r["id"], r.get("title"), r.get("price"), r.get("url"),
                    ])
            print(f"{name}: {len(changed)} changed of {len(rows)} fetched")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--db", default="data/watch.db")
    args = ap.parse_args()
    run(args.config, args.db)
