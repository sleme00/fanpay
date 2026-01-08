import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fanpay_bot.models import Listing


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: int
    created_at: str


class SnapshotStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._init_db()

    def _init_db(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS listings (
                    snapshot_id INTEGER NOT NULL,
                    listing_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    category_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    sold_24h INTEGER NOT NULL,
                    FOREIGN KEY(snapshot_id) REFERENCES snapshots(id)
                )
                """
            )

    def create_snapshot(self, created_at: str, listings: Iterable[Listing]) -> Snapshot:
        listings = list(listings)
        with sqlite3.connect(self._path) as conn:
            cur = conn.execute("INSERT INTO snapshots (created_at) VALUES (?)", (created_at,))
            snapshot_id = cur.lastrowid
            conn.executemany(
                """
                INSERT INTO listings (
                    snapshot_id, listing_id, game_id, category_id, title, price, currency, quantity, sold_24h
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        snapshot_id,
                        item.listing_id,
                        item.game_id,
                        item.category_id,
                        item.title,
                        item.price,
                        item.currency,
                        item.quantity,
                        item.sold_24h,
                    )
                    for item in listings
                ],
            )
        return Snapshot(snapshot_id=snapshot_id, created_at=created_at)

    def get_latest_snapshot_id(self) -> int | None:
        with sqlite3.connect(self._path) as conn:
            row = conn.execute("SELECT id FROM snapshots ORDER BY created_at DESC LIMIT 1").fetchone()
        return int(row[0]) if row else None

    def get_previous_snapshot_id(self, latest_snapshot_id: int) -> int | None:
        with sqlite3.connect(self._path) as conn:
            row = conn.execute(
                "SELECT id FROM snapshots WHERE id < ? ORDER BY id DESC LIMIT 1",
                (latest_snapshot_id,),
            ).fetchone()
        return int(row[0]) if row else None

    def fetch_listings(self, snapshot_id: int) -> list[Listing]:
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                """
                SELECT listing_id, game_id, category_id, title, price, currency, quantity, sold_24h
                FROM listings
                WHERE snapshot_id = ?
                """,
                (snapshot_id,),
            ).fetchall()
        return [
            Listing(
                listing_id=row[0],
                game_id=row[1],
                category_id=row[2],
                title=row[3],
                price=float(row[4]),
                currency=row[5],
                quantity=int(row[6]),
                sold_24h=int(row[7]),
            )
            for row in rows
        ]
