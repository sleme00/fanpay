from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fanpay_bot.analytics import CategoryReport, rank_categories, summarize_category
from fanpay_bot.datasource import DataSource, SqliteDataSource
from fanpay_bot.models import Category, Game, Listing
from fanpay_bot.storage import Snapshot, SnapshotStore


@dataclass(frozen=True)
class SnapshotResult:
    snapshot: Snapshot
    total_listings: int


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9а-яё]+", "-", value, flags=re.IGNORECASE)
    return value.strip("-") or "game"


class FanPayService:
    def __init__(self, data_source: DataSource, store: SnapshotStore) -> None:
        self._data_source = data_source
        self._store = store

    @classmethod
    def from_config(cls, data_source: str, sample_data_path: Path, sqlite_path: Path) -> "FanPayService":
        if data_source == "sqlite":
            source = SqliteDataSource(sqlite_path)
            store = source.store
        else:
            raise ValueError("Only sqlite data source is configured.")
        service = cls(source, store)
        service._maybe_seed_sample(sample_data_path)
        return service

    def _maybe_seed_sample(self, sample_data_path: Path) -> None:
        if self.list_games():
            return
        if not sample_data_path.exists():
            return
        payload = json.loads(sample_data_path.read_text(encoding="utf-8"))
        for item in payload.get("games", []):
            self.create_game(item["name"], game_id=item["id"])
        for game_id, categories in payload.get("categories", {}).items():
            for category in categories:
                self.create_category(
                    game_id=game_id,
                    name=category["name"],
                    item_type=category.get("type"),
                    category_id=category["id"],
                )
        for game_id, categories in payload.get("listings", {}).items():
            for category_id, listings in categories.items():
                for listing in listings:
                    self.create_listing(
                        game_id=game_id,
                        category_id=category_id,
                        title=listing["title"],
                        price=float(listing["price"]),
                        currency=listing.get("currency", "RUB"),
                        quantity=int(listing.get("quantity", 1)),
                        sold_24h=int(listing.get("sold_24h", 0)),
                        listing_id=listing["id"],
                    )

    def list_games(self, search: str | None = None) -> list[Game]:
        return self._data_source.list_games(search)

    def list_categories(self, game_id: str) -> list[Category]:
        return self._data_source.list_categories(game_id)

    def list_listings(self, game_id: str, category_id: str) -> list[Listing]:
        return self._data_source.list_listings(game_id, category_id)

    def create_game(self, name: str, game_id: str | None = None) -> Game:
        game_id = game_id or _slugify(name)
        game = Game(game_id=game_id, name=name)
        self._store.upsert_game(game)
        return game

    def create_category(
        self,
        game_id: str,
        name: str,
        item_type: str | None = None,
        category_id: str | None = None,
    ) -> Category:
        category_id = category_id or f"{game_id}-{_slugify(name)}"
        category = Category(
            category_id=category_id,
            game_id=game_id,
            name=name,
            item_type=item_type,
        )
        self._store.upsert_category(category)
        return category

    def create_listing(
        self,
        game_id: str,
        category_id: str,
        title: str,
        price: float,
        currency: str,
        quantity: int,
        sold_24h: int,
        listing_id: str | None = None,
    ) -> Listing:
        listing_id = listing_id or f"{category_id}-{_slugify(title)}"
        listing = Listing(
            listing_id=listing_id,
            game_id=game_id,
            category_id=category_id,
            title=title,
            price=price,
            currency=currency,
            quantity=quantity,
            sold_24h=sold_24h,
        )
        self._store.upsert_listing_data(listing)
        return listing

    def capture_snapshot(self, game_id: str, category_ids: list[str]) -> SnapshotResult:
        listings: list[Listing] = []
        for category_id in category_ids:
            listings.extend(self._data_source.list_listings(game_id, category_id))
        timestamp = datetime.now(timezone.utc).isoformat()
        snapshot = self._store.create_snapshot(timestamp, listings)
        return SnapshotResult(snapshot=snapshot, total_listings=len(listings))

    def analyze_categories(self, game_id: str, category_ids: list[str]) -> list[CategoryReport]:
        latest_id = self._store.get_latest_snapshot_id()
        if latest_id is None:
            raise RuntimeError("Нет сохраненных снапшотов. Сначала сделай снапшот.")
        previous_id = self._store.get_previous_snapshot_id(latest_id)
        latest_listings = self._store.fetch_listings(latest_id)
        previous_listings = self._store.fetch_listings(previous_id) if previous_id else []

        categories = {item.category_id: item for item in self.list_categories(game_id)}
        reports: list[CategoryReport] = []
        for category_id in category_ids:
            current = [item for item in latest_listings if item.category_id == category_id]
            previous = [item for item in previous_listings if item.category_id == category_id]
            category = categories.get(category_id)
            category_name = category.name if category else category_id
            report = summarize_category(current, previous, category_id, category_name)
            reports.append(report)

        return rank_categories(reports)
