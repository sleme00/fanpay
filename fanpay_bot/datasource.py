import json
from pathlib import Path
from typing import Protocol

from fanpay_bot.models import Category, Game, Listing


class DataSource(Protocol):
    def list_games(self) -> list[Game]:
        raise NotImplementedError

    def list_categories(self, game_id: str) -> list[Category]:
        raise NotImplementedError

    def list_listings(self, game_id: str, category_id: str) -> list[Listing]:
        raise NotImplementedError


class MockDataSource:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._payload = self._load_payload()

    def _load_payload(self) -> dict:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Sample data not found at {self._path}. "
                "Set FANPAY_SAMPLE_DATA to a valid JSON file."
            )
        return json.loads(self._path.read_text(encoding="utf-8"))

    def list_games(self) -> list[Game]:
        return [Game(game_id=item["id"], name=item["name"]) for item in self._payload["games"]]

    def list_categories(self, game_id: str) -> list[Category]:
        return [
            Category(
                category_id=item["id"],
                game_id=game_id,
                name=item["name"],
                item_type=item.get("type"),
            )
            for item in self._payload["categories"].get(game_id, [])
        ]

    def list_listings(self, game_id: str, category_id: str) -> list[Listing]:
        listings = self._payload["listings"].get(game_id, {}).get(category_id, [])
        return [
            Listing(
                listing_id=item["id"],
                game_id=game_id,
                category_id=category_id,
                title=item["title"],
                price=float(item["price"]),
                currency=item.get("currency", "RUB"),
                quantity=int(item.get("quantity", 1)),
                sold_24h=int(item.get("sold_24h", 0)),
            )
            for item in listings
        ]
