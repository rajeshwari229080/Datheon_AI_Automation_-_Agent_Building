import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Production application settings with environment variable bindings."""

    # Application details
    app_name: str = "Enterprise AI Automation Suite"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_secret_key: str = Field(default="dev-secret-key-replace-in-production", alias="APP_SECRET_KEY")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database
    database_url: str = Field(default="sqlite:///./enterprise_suite.db", alias="DATABASE_URL")

    # Mode switch: When True, mock adapters simulate external dependencies without throwing errors
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")

    # AI / LLM
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_vision_model: str = Field(default="gpt-4o", alias="OPENAI_VISION_MODEL")

    # Module 1: Airtable
    airtable_api_key: Optional[str] = Field(default=None, alias="AIRTABLE_API_KEY")
    airtable_base_id: Optional[str] = Field(default=None, alias="AIRTABLE_BASE_ID")
    airtable_table_name: str = Field(default="Leads", alias="AIRTABLE_TABLE_NAME")

    # Module 1 & 4: Slack
    slack_bot_token: Optional[str] = Field(default=None, alias="SLACK_BOT_TOKEN")
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    slack_default_channel: str = Field(default="#enterprise-alerts", alias="SLACK_DEFAULT_CHANNEL")

    # Module 2: Email Triage
    email_provider: str = Field(default="mock", alias="EMAIL_PROVIDER")
    email_smtp_host: Optional[str] = Field(default=None, alias="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(default=587, alias="EMAIL_SMTP_PORT")
    email_user: Optional[str] = Field(default=None, alias="EMAIL_USER")
    email_password: Optional[str] = Field(default=None, alias="EMAIL_PASSWORD")

    # Module 3: Google Sheets
    google_service_account_json: Optional[str] = Field(default=None, alias="GOOGLE_SERVICE_ACCOUNT_JSON")
    google_sheet_id: Optional[str] = Field(default=None, alias="GOOGLE_SHEET_ID")

    # Module 4: Stripe
    stripe_api_key: Optional[str] = Field(default=None, alias="STRIPE_API_KEY")
    stripe_webhook_secret: str = Field(default="whsec_test_secret_for_local_testing_12345", alias="STRIPE_WEBHOOK_SECRET")

    # Security & Upload constraints
    max_upload_size_bytes: int = 15 * 1024 * 1024  # 15 MB
    allowed_upload_mime_types: list[str] = ["application/pdf", "image/png", "image/jpeg", "image/webp"]
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def mask_secret(value: Optional[str]) -> str:
    """Mask sensitive tokens for safe logging and status reporting."""
    if not value:
        return "<not set>"
    if len(value) <= 8:
        return "****"
    return f"{value[:3]}****{value[-4:]}"

# Global settings instance
settings = Settings()

# Configure structured enterprise logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("enterprise_suite")
