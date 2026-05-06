"""Central configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./data/entities.db")

    # Socrata / open-data API URLs (overridable)
    HAWAII_API_URL: str = os.environ.get(
        "HAWAII_API_URL",
        "https://data.honolulu.gov/resource/9k54-ztb8.json",
    )
    CONNECTICUT_API_URL: str = os.environ.get(
        "CONNECTICUT_API_URL",
        "https://data.ct.gov/resource/n7gm-hh35.json",
    )
    LA_API_URL: str = os.environ.get(
        "LA_API_URL",
        "https://data.lacity.org/resource/r4uk-afju.json",
    )
    # Apify actor for Wyoming SOS
    WYOMING_APIFY_TOKEN: str = os.environ.get("WYOMING_APIFY_TOKEN", "")
    WYOMING_APIFY_ACTOR: str = os.environ.get(
        "WYOMING_APIFY_ACTOR", "parseforge/wyoming-business-scraper"
    )

    # Socrata app token (optional, increases rate limits)
    SOCRATA_APP_TOKEN: str = os.environ.get("SOCRATA_APP_TOKEN", "")

    # Collection
    DEFAULT_LIMIT: int = int(os.environ.get("DEFAULT_LIMIT", "500"))
    TARGET_DATE: str = os.environ.get("TARGET_DATE", "")
    OUTPUT_CSV_DIR: str = os.environ.get("OUTPUT_CSV_DIR", "data/exports")

    # Enabled sources (comma-separated): hawaii, connecticut, los_angeles, wyoming
    ENABLED_SOURCES: list[str] = [
        s.strip()
        for s in os.environ.get("ENABLED_SOURCES", "hawaii,connecticut,los_angeles").split(",")
        if s.strip()
    ]

    # API server
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.environ.get("API_PORT", "8000"))
    CORS_ORIGINS: list[str] = [
        s.strip()
        for s in os.environ.get(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",")
        if s.strip()
    ]

    # Scheduler (cron, 24h format UTC)
    SCHEDULER_HOUR: int = int(os.environ.get("SCHEDULER_HOUR", "0"))
    SCHEDULER_MINUTE: int = int(os.environ.get("SCHEDULER_MINUTE", "5"))

    # Domain check rate limit (seconds between RDAP requests)
    DOMAIN_CHECK_DELAY: float = float(os.environ.get("DOMAIN_CHECK_DELAY", "0.5"))


settings = Settings()
