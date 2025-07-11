"""
src/schemas/enums.py

Enum definitions for complaint status, sentiment, and category with rich
docstrings and inline comments for autogenerated documentation.
"""

from enum import Enum


class StatusEnum(str, Enum):
    """
    Enumeration of complaint statuses.

    Attributes:
        OPEN: Complaint is open and awaiting processing.
        CLOSED: Complaint has been processed and closed.
    """

    OPEN = "open"  # Open status
    CLOSED = "closed"  # Closed status


class SentimentEnum(str, Enum):
    """
    Enumeration of sentiment analysis results.

    Attributes:
        POSITIVE: Positive sentiment.
        NEGATIVE: Negative sentiment.
        NEUTRAL: Neutral sentiment.
        UNKNOWN: Sentiment could not be determined.
    """

    POSITIVE = "positive"  # Indicates positive sentiment
    NEGATIVE = "negative"  # Indicates negative sentiment
    NEUTRAL = "neutral"  # Indicates neutral sentiment
    UNKNOWN = "unknown"  # Sentiment unknown or API failure


class CategoryEnum(str, Enum):
    """
    Enumeration of complaint categories.

    Attributes:
        TECHNICAL: Technical issues category.
        PAYMENT: Payment-related issues category.
        OTHER: Other types of complaints.
    """

    TECHNICAL = "technical"  # Technical complaint
    PAYMENT = "payment"  # Payment complaint
    OTHER = "other"  # Other complaint
