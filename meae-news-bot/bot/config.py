"""Settings, read from environment variables (or a .env file)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return int(value) if value else default


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: frozenset[int]
    db_path: str = "data/meae_news.db"
    # How often every RSS feed is checked. 180s keeps alerts under ~5 minutes.
    poll_interval: int = 180
    google_news_enabled: bool = True
    google_news_interval: int = 600
    max_keywords: int = 10
    # Articles older than this are stored (for search) but never alerted.
    max_article_age_hours: int = 12
    retention_days: int = 30
    default_timezone: str = "Asia/Riyadh"


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")
    admins = frozenset(
        int(part) for part in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if part
    )
    return Config(
        bot_token=token,
        admin_ids=admins,
        db_path=os.getenv("DB_PATH", "data/meae_news.db"),
        poll_interval=_int("POLL_INTERVAL_SECONDS", 180),
        google_news_enabled=_bool("GOOGLE_NEWS_ENABLED", True),
        google_news_interval=_int("GOOGLE_NEWS_INTERVAL_SECONDS", 600),
        max_keywords=_int("MAX_KEYWORDS_PER_USER", 10),
        max_article_age_hours=_int("MAX_ARTICLE_AGE_HOURS", 12),
        retention_days=_int("RETENTION_DAYS", 30),
        default_timezone=os.getenv("DEFAULT_TIMEZONE", "Asia/Riyadh"),
    )
