from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fanpay_bot.analytics import CategoryReport, rank_categories, summarize_category
from fanpay_bot.datasource import DataSource, MockDataSource
from fanpay_bot.models import Category, Game, Listing
from fanpay_bot.storage import Snapshot, SnapshotStore


@dataclass(frozen=True)
class SnapshotResult:
    snapshot: Snapshot
    total_listings: int


class FanPayService:
    def __init__(self, data_source: DataSource, store: SnapshotStore) -> None:
        self._data_source = data_source
        self._store = store

    @classmethod
    def from_config(cls, data_source: str, sample_data_path: Path, sqlite_path: Path) -> "FanPayService":
        if data_source == "mock":
            source = MockDataSource(sample_data_path)
        else:
            raise ValueError(
                "Only mock data source is configured. "
                "Set FANPAY_DATA_SOURCE=mock or implement another adapter."
            )
        return cls(source, SnapshotStore(sqlite_path))

    def list_games(self) -> list[Game]:
        return self._data_source.list_games()

    def list_categories(self, game_id: str) -> list[Category]:
        return self._data_source.list_categories(game_id)

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
            raise RuntimeError("No snapshots saved yet. Run !snapshot first.")
        previous_id = self._store.get_previous_snapshot_id(latest_id)
        latest_listings = self._store.fetch_listings(latest_id)
        previous_listings = self._store.fetch_listings(previous_id) if previous_id else []

        reports: list[CategoryReport] = []
        for category_id in category_ids:
            current = [item for item in latest_listings if item.category_id == category_id]
            previous = [item for item in previous_listings if item.category_id == category_id]
            report = summarize_category(current, previous)
            reports.append(report)

        return rank_categories(reports)
