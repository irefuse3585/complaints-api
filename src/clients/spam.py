# src/clients/spam.py

"""
Client for APILayer Spam Checker API.

Provides an asynchronous helper to check whether a given text is spam.
Handles all network and API errors gracefully, always returning a boolean.
"""

import logging

import httpx

from src.config import settings

API_URL = "https://api.apilayer.com/spamchecker"

logger = logging.getLogger(__name__)


async def check_spam(text: str) -> bool:
    """
    Check if the given text is classified as spam via APILayer Spam Checker.

    Sends the text as plain content with an optional threshold query param.
    Returns True if API marks it as spam, False otherwise (including on error).

    Args:
        text: the input text to evaluate
        threshold: spam sensitivity (1–10; lower means more aggressive)

    Returns:
        bool: True if spam, False if not or on failure
    """
    headers = {
        "apikey": settings.spam_api_key,
        "Content-Type": "text/plain",
    }
    # build URL with threshold parameter
    url = f"{API_URL}?threshold={settings.threshold}"

    # configure timeouts: 2s connect, 5s read, total 8s
    timeout = httpx.Timeout(timeout=8.0, connect=2.0, read=5.0)

    logger.debug("Spam check request (first 100 chars): %r", text[:100])
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, content=text)
            response.raise_for_status()

        payload = response.json()
        # response fields: is_spam (bool),
        # score (float), result (str), text (str)
        is_spam = bool(payload.get("is_spam", False))
        score = payload.get("score")
        logger.info("Spam API response: is_spam=%s, score=%s", is_spam, score)
        return is_spam

    except httpx.HTTPStatusError as exc:
        # API returned 4xx or 5xx
        logger.error(
            "Spam API HTTP %s error: %s",
            exc.response.status_code,
            exc,
            exc_info=True,  # noqa: E501
        )  # noqa: E501
    except httpx.RequestError as exc:
        # network error, timeout, DNS failure, etc.
        logger.error("Spam API request failed: %s", exc, exc_info=True)
    except ValueError as exc:
        # JSON decoding error
        logger.error("Invalid JSON from Spam API: %s", exc, exc_info=True)
    except Exception as exc:
        # catch-all for unexpected errors
        logger.error("Unexpected error in spam client: %s", exc, exc_info=True)

    logger.warning(
        "Returning False (not spam) due to error for text: %r", text[:40]
    )  # noqa: E501
    return False
