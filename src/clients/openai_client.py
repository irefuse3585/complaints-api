"""
src/clients/openai_client.py

Client for classifying complaint text using OpenAI’s official Python SDK
(>=1.93.0) with AsyncOpenAI, including safety against missing content.
"""

import logging

from openai import AsyncOpenAI

from ..config import settings
from ..schemas.enums import CategoryEnum  # type: ignore[attr-defined]

logger = logging.getLogger(__name__)

# Instantiate a shared async client with your API key
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def categorize_complaint(text: str) -> CategoryEnum:
    """
    Classify a complaint into one of three categories using GPT-3.5 Turbo.

    Uses `await client.chat.completions.create(...)`
    per the official async example:
    https://github.com/openai/openai-python#async-usage

    Args:
        text (str): The complaint text to classify.

    Returns:
        CategoryEnum: TECHNICAL, PAYMENT, or OTHER.
    """
    messages = [
        {"role": "system", "content": "You are a classification assistant."},
        {
            "role": "user",
            "content": (
                f'Определи категорию жалобы: "{text}". '
                "Варианты: техническая, оплата, другое. Ответь одним словом."
            ),
        },
    ]  # type: ignore[list-item]

    logger.debug(
        "Sending prompt to OpenAI for classification: %s",
        messages[1]["content"][:120],  # noqa: E501
    )  # noqa: E501
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,  # type: ignore[arg-type]
            temperature=0,
        )
        raw = response.choices[0].message.content
        answer = (raw or "").strip().lower()
        logger.info(
            "OpenAI classified complaint as: '%s' (raw='%s')", answer, raw
        )  # noqa: E501

        if "техничес" in answer or answer.startswith("technical"):
            return CategoryEnum.TECHNICAL
        if "оплат" in answer or answer.startswith("payment"):
            return CategoryEnum.PAYMENT
    except Exception as e:
        logger.error("OpenAI classification failed: %s", e, exc_info=True)

    logger.warning(
        "OpenAI returned unknown or missing category for text: %s", text[:120]
    )
    return CategoryEnum.OTHER
