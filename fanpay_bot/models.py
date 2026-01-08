from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    game_id: str
    name: str


@dataclass(frozen=True)
class Category:
    category_id: str
    game_id: str
    name: str
    item_type: str | None = None


@dataclass(frozen=True)
class Listing:
    listing_id: str
    game_id: str
    category_id: str
    title: str
    price: float
    currency: str
    quantity: int
    sold_24h: int
