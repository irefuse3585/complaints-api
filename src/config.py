"""
src/config.py

Application settings loaded from environment variables or a .env file,
using Pydantic v2 pydantic-settings, with explicit __init__ to satisfy type
checkers and avoid “missing arguments” errors.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration parameters for the application.

    Values are resolved in this order:
    1. Keyword args to Settings()
    2. Environment variables (UPPER_SNAKE_CASE)
    3. .env file variables
    4. Field default values
    """

    # Tell pydantic where to load `.env`
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        ...,
        description="SQLAlchemy database URL",
    )
    sentiment_api_key: str = Field(
        ..., description="API key for Sentiment Analysis by APILayer"
    )
    spam_api_key: str = Field(
        ..., description="API key for Spam Check by API Ninjas"
    )  # noqa: E501
    openai_api_key: str = Field(
        ...,
        description="API key for OpenAI GPT (used to classify complaint category)",  # noqa: E501
    )
    ip_api_url: str = Field(
        "http://ip-api.com/json",
        description="Base URL for IP geolocation API (no key required)",
    )
    log_level: str = Field(
        "INFO",
        description="Log level for application logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)",  # noqa: E501
    )
    threshold: float = Field(5, description="Threshold for spam api(1-10)")

    def __init__(self, **kwargs):
        """
        Explicit no-arg __init__ so static type checkers
        don’t require positional arguments.
        """
        super().__init__(**kwargs)


# Instantiate once; import `settings` wherever needed
settings = Settings()
