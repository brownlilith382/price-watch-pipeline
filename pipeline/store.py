"""SQLite store: one row per listing, plus a price history table."""

import sqlite3
import time


SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    source TEXT NOT NULL,
    listing_id TEXT NOT NULL,
    title TEXT,
    price REAL,
    currency TEXT,
    url TEXT,
    first_seen INTEGER,
    last_seen INTEGER,
    price_changed INTEGER DEFAULT 0,
    PRIMARY KEY (source, listing_id)
);
CREATE TABLE IF NOT EXISTS price_history (
    source TEXT NOT NULL,
    listing_id TEXT NOT NULL,
    ts INTEGER NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (source, listing_id, ts)
);
"""


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def upsert(self, source: str, rows: list) -> list:
        """Insert/update listings. Returns rows that are new or changed price."""
        now = int(time.time())
        changed = []
        for r in rows:
            cur = self.db.execute(
                "SELECT price FROM listings WHERE source = ? AND listing_id = ?",
                (source, r["id"]),
            )
            old = cur.fetchone()
            if old is None:
                self.db.execute(
                    "INSERT INTO listings (source, listing_id, title, price, currency, url,"
                    " first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (source, r["id"], r.get("title"), r.get("price"), r.get("currency"),
                     r.get("url"), now, now),
                )
                changed.append(r)
            elif r.get("price") is not None and (old[0] is None or abs(old[0] - r["price"]) > 0.005):
                self.db.execute(
                    "UPDATE listings SET price = ?, last_seen = ?, price_changed = 1"
                    " WHERE source = ? AND listing_id = ?",
                    (r["price"], now, source, r["id"]),
                )
                self.db.execute(
                    "INSERT INTO price_history (source, listing_id, ts, price) VALUES (?, ?, ?, ?)",
                    (source, r["id"], now, r["price"]),
                )
                changed.append(r)
            else:
                self.db.execute(
                    "UPDATE listings SET last_seen = ? WHERE source = ? AND listing_id = ?",
                    (now, source, r["id"]),
                )
        self.db.commit()
        return changed
