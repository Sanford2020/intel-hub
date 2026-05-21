import json

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_name: str = "intel-hub"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000

    database_url: str = "postgresql://postgres:postgres@localhost:5432/intel_hub"

    redis_url: str = "redis://localhost:6379/0"

    cors_origins_env: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    secret_key: str = "change-this-to-a-random-secret-key"  # noqa: S105
    access_token_expire_minutes: int = 30

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    log_level: str = "INFO"
    log_format: str = "console"

    prompts_dir: str = "../prompts"

    ingest_default_interval_minutes: int = 30
    intel_prompt_template: str = "intelligence/analyze"
    briefing_min_relevance: float = Field(default=6.0, alias="BRIEFING_MIN_RELEVANCE")

    # Briefing push (Feishu / n8n / Telegram)
    briefing_push_enabled: bool = Field(default=True, alias="BRIEFING_PUSH_ENABLED")
    feishu_webhook_url: str = Field(default="", alias="FEISHU_WEBHOOK_URL")
    feishu_push_top_n: int = Field(default=5, alias="FEISHU_PUSH_TOP_N")
    briefing_public_base_url: str = Field(
        default="http://localhost:3000",
        alias="BRIEFING_PUBLIC_BASE_URL",
    )
    n8n_webhook_url: str = Field(default="", alias="N8N_WEBHOOK_URL")
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")

    # RSSHub (self-hosted X → RSS)
    rsshub_base_url: str = Field(default="http://localhost:1200", alias="RSSHUB_BASE_URL")

    # Apify X scraper
    apify_token: str = Field(default="", alias="APIFY_TOKEN")
    apify_twitter_actor: str = Field(
        default="apidojo~tweet-scraper",
        alias="APIFY_TWITTER_ACTOR",
    )

    # AI HOT REST API
    aihot_api_base: str = Field(
        default="https://aihot.virxact.com",
        alias="AIHOT_API_BASE",
    )

    # X (Twitter): official API when set, else RSS bridge (e.g. rss.xcancel.com)
    x_bearer_token: str = Field(default="", alias="X_BEARER_TOKEN")
    x_rss_bridge_base: str = Field(
        default="https://rss.xcancel.com",
        alias="X_RSS_BRIDGE_BASE",
    )
    # Bird / last30days-style X session cookies (from x.com: auth_token + ct0)
    x_auth_token: str = Field(default="", alias="X_AUTH_TOKEN")
    x_ct0: str = Field(default="", alias="X_CT0")
    http_ssl_verify: bool = Field(default=True, alias="HTTP_SSL_VERIFY")

    # Daily archive (Beijing calendar day)
    archive_enabled: bool = Field(default=True, alias="ARCHIVE_ENABLED")
    archive_timezone: str = Field(default="Asia/Shanghai", alias="ARCHIVE_TIMEZONE")
    archive_window_hours: int = Field(default=24, alias="ARCHIVE_WINDOW_HOURS")
    archive_briefing_limit: int = Field(default=20, alias="ARCHIVE_BRIEFING_LIMIT")
    archive_min_relevance: float = Field(default=6.0, alias="ARCHIVE_MIN_RELEVANCE")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_env.strip()
        if raw.startswith("["):
            return json.loads(raw)
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
