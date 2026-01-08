import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotConfig:
    data_source: str
    sample_data_path: Path
    sqlite_path: Path


def load_config() -> BotConfig:
    data_source = os.getenv("FANPAY_DATA_SOURCE", "sqlite").strip().lower()
    sample_data_path = Path(os.getenv("FANPAY_SAMPLE_DATA", "fanpay_bot/data/sample_data.json"))
    sqlite_path = Path(os.getenv("FANPAY_SQLITE_PATH", "fanpay_bot/data/snapshots.db"))

    return BotConfig(
        data_source=data_source,
        sample_data_path=sample_data_path,
        sqlite_path=sqlite_path,
    )
