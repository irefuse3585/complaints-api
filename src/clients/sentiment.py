# src/clients/sentiment.py

"""
Client for APILayer Sentiment Analysis API.

Provides an asynchronous helper to analyze sentiment for arbitrary text.
Handles network errors and unexpected responses gracefully,
always returning a valid SentimentEnum.
"""

import logging
from typing import Mapping

import httpx

from src.config import settings
from src.schemas.enums import SentimentEnum  # type: ignore[attr-defined]

API_URL = "https://api.apilayer.com/sentiment/analysis"

# map the API’s sentiment strings to our enum values
_SENTIMENT_MAP: Mapping[str, SentimentEnum] = {
    "positive": SentimentEnum.POSITIVE,
    "negative": SentimentEnum.NEGATIVE,
    "neutral": SentimentEnum.NEUTRAL,
}

logger = logging.getLogger(__name__)


async def get_sentiment(text: str) -> SentimentEnum:
    """
    Analyze the sentiment of the given text using
    APILayer's Sentiment Analysis API.

    Sends the text as plain content (Content-Type: text/plain).
    Returns one of POSITIVE, NEGATIVE,
    NEUTRAL, or UNKNOWN if anything goes wrong.

    Args:
        text: the input text to analyze

    Returns:
        SentimentEnum: mapped sentiment or UNKNOWN
    """
    headers = {
        "apikey": settings.sentiment_api_key,
        "Content-Type": "text/plain",
    }

    # configure timeouts: 2s connect, 5s read, total 8s
    timeout = httpx.Timeout(timeout=8.0, connect=2.0, read=5.0)

    logger.debug(
        "Calling Sentiment API for text (first 100 chars): %r", text[:100]
    )  # noqa: E501
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                API_URL, headers=headers, content=text
            )  # noqa: E501
            response.raise_for_status()

        payload = response.json()
        raw_sentiment = payload.get("sentiment", "")
        key = raw_sentiment.lower()
        logger.info("API returned sentiment=%r", key)

        # return mapped enum or default to UNKNOWN
        return _SENTIMENT_MAP.get(key, SentimentEnum.UNKNOWN)

    except httpx.HTTPStatusError as exc:
        # API returned 4xx or 5xx
        logger.error(
            "Sentiment API HTTP %s error: %s",
            exc.response.status_code,
            exc,
            exc_info=True,
        )
    except httpx.RequestError as exc:
        # network error, timeout, DNS failure, etc.
        logger.error("Sentiment API request failed: %s", exc, exc_info=True)
    except ValueError as exc:
        # JSON decoding failed
        logger.error("Invalid JSON from Sentiment API: %s", exc, exc_info=True)
    except Exception as exc:
        # any other unexpected error
        logger.error(
            "Unexpected error in sentiment client: %s", exc, exc_info=True
        )  # noqa: E501

    logger.warning("Returning UNKNOWN sentiment for text start: %r", text[:40])
    return SentimentEnum.UNKNOWN
