from pathlib import Path
from typing import Protocol

from fanpay_bot.models import Category, Game, Listing
from fanpay_bot.storage import SnapshotStore


class DataSource(Protocol):
    def list_games(self, search: str | None = None) -> list[Game]:
        raise NotImplementedError

    def list_categories(self, game_id: str) -> list[Category]:
        raise NotImplementedError

    def list_listings(self, game_id: str, category_id: str) -> list[Listing]:
        raise NotImplementedError


class SqliteDataSource:
    def __init__(self, path: Path) -> None:
        self._store = SnapshotStore(path)

    def list_games(self, search: str | None = None) -> list[Game]:
        return self._store.list_games(search)

    def list_categories(self, game_id: str) -> list[Category]:
        return self._store.list_categories(game_id)

    def list_listings(self, game_id: str, category_id: str) -> list[Listing]:
        return self._store.list_listing_data(game_id, category_id)

    @property
    def store(self) -> SnapshotStore:
        return self._store
