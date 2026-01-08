from dataclasses import dataclass
from statistics import median
from typing import Iterable

from fanpay_bot.models import Listing


@dataclass(frozen=True)
class CategoryReport:
    category_id: str
    listing_count: int
    average_price: float
    median_price: float
    min_price: float
    max_price: float
    avg_sold_24h: float
    demand_score: float
    price_change_pct: float | None


def _safe_average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_category(current: Iterable[Listing], previous: Iterable[Listing]) -> CategoryReport:
    current_list = list(current)
    prices = [item.price for item in current_list]
    sold = [item.sold_24h for item in current_list]
    listing_count = len(current_list)
    average_price = _safe_average(prices)
    median_price = float(median(prices)) if prices else 0.0
    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0
    avg_sold_24h = _safe_average(sold)
    demand_score = avg_sold_24h / average_price if average_price else 0.0

    previous_prices = [item.price for item in previous]
    previous_average = _safe_average(previous_prices)
    if previous_average and average_price:
        price_change_pct = ((average_price - previous_average) / previous_average) * 100
    else:
        price_change_pct = None

    return CategoryReport(
        category_id=current_list[0].category_id if current_list else "",
        listing_count=listing_count,
        average_price=average_price,
        median_price=median_price,
        min_price=min_price,
        max_price=max_price,
        avg_sold_24h=avg_sold_24h,
        demand_score=demand_score,
        price_change_pct=price_change_pct,
    )


def rank_categories(reports: Iterable[CategoryReport]) -> list[CategoryReport]:
    return sorted(
        reports,
        key=lambda report: (report.demand_score, report.avg_sold_24h, report.average_price),
        reverse=True,
    )
