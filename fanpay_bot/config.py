import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotConfig:
    discord_token: str
    data_source: str
    sample_data_path: Path
    sqlite_path: Path
    snapshot_channel_id: int | None
    snapshot_hour_utc: int


def load_config() -> BotConfig:
    discord_token = os.getenv("DISCORD_TOKEN", "").strip()
    data_source = os.getenv("FANPAY_DATA_SOURCE", "mock").strip().lower()
    sample_data_path = Path(os.getenv("FANPAY_SAMPLE_DATA", "fanpay_bot/data/sample_data.json"))
    sqlite_path = Path(os.getenv("FANPAY_SQLITE_PATH", "fanpay_bot/data/snapshots.db"))
    snapshot_channel_id = os.getenv("FANPAY_SNAPSHOT_CHANNEL_ID")
    snapshot_hour_utc = int(os.getenv("FANPAY_SNAPSHOT_HOUR_UTC", "6"))

    return BotConfig(
        discord_token=discord_token,
        data_source=data_source,
        sample_data_path=sample_data_path,
        sqlite_path=sqlite_path,
        snapshot_channel_id=int(snapshot_channel_id) if snapshot_channel_id else None,
        snapshot_hour_utc=snapshot_hour_utc,
    )
