"""
src/services/complaint_service.py

ComplaintService provides business logic for handling customer complaints.
Includes orchestration of external APIs for sentiment analysis (APILayer),
spam check (API Ninjas), and category classification (OpenAI).
All error handling and fallback logic are managed here.

This service is designed for asynchronous use with FastAPI and SQLAlchemy.
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..clients.geoip import get_geolocation
from ..clients.openai_client import categorize_complaint
from ..clients.sentiment import get_sentiment
from ..clients.spam import check_spam
from ..models.complaint import Complaint
from ..schemas.complaint import ComplaintCreate, ComplaintResponse
from ..schemas.enums import CategoryEnum, SentimentEnum, StatusEnum

logger = logging.getLogger(__name__)


class ComplaintService:
    """
    Service for handling business logic related to customer complaints.

    Responsibilities:
        - Persist new complaint records in the database.
        - Integrate with APILayer for sentiment analysis.
        - Integrate with API Ninjas for spam checking.
        - Classify complaint category using OpenAI (GPT-3.5 Turbo).
        - Provide robust error handling and fallback behaviors.
        - Retrieve and filter complaints.
        - Update complaint status.
    """

    def __init__(
        self,
        session: AsyncSession,
        enable_spam_check: bool = True,
    ):
        """
        Initialize the ComplaintService.

        Args:
            session (AsyncSession): Async SQLAlchemy session.
            enable_spam_check (bool): Whether to use spam checking.
        """
        self.session = session
        self.enable_spam_check = enable_spam_check

    async def create_complaint(
        self, data: ComplaintCreate, client_ip: Optional[str] = None
    ) -> ComplaintResponse:
        """
        Create a new complaint record in the database, analyzing sentiment,
        checking for spam, and classifying the complaint category.

        Args:
            data (ComplaintCreate): Input data for the complaint.

        Returns:
            ComplaintResponse: Response schema including all relevant fields.
        """
        logger.info("Creating new complaint: %s", data.text[:120])
        # Step 1: Sentiment analysis via APILayer
        try:
            sentiment = await get_sentiment(data.text)
            logger.debug("Sentiment analysis result: %s", sentiment)
        except Exception as e:
            sentiment = SentimentEnum.UNKNOWN
            logger.error("Sentiment API failed: %s", e, exc_info=True)

        # Step 2: Spam check using API Ninjas (result not stored)
        if self.enable_spam_check:
            try:
                await check_spam(data.text)
                logger.debug("Spam check passed for complaint")
            except Exception as e:
                logger.error("Spam check API failed: %s", e, exc_info=True)

        # Step 2.5: Geolocation lookup by IP (no persistence)
        if client_ip:
            try:
                await get_geolocation(client_ip)
                logger.debug("GeoIP lookup done for %s", client_ip)
            except Exception as e:
                logger.error(
                    "GeoIP lookup failed for %s: %s", client_ip, e, exc_info=True
                )

        # Step 3: Persist the complaint with initial fields (category OTHER)
        complaint = Complaint(
            text=data.text,
            status=StatusEnum.OPEN,
            sentiment=sentiment,
            category=CategoryEnum.OTHER,
        )
        self.session.add(complaint)
        try:
            await self.session.commit()
            await self.session.refresh(complaint)
            logger.info("Complaint created in DB with id=%s", complaint.id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.critical("DB error during complaint creation: %s", e, exc_info=True)
            raise

        # Step 4: Classify the complaint category using OpenAI
        try:
            category = await categorize_complaint(data.text)
            logger.debug("Complaint categorized: %s", category)
        except Exception as e:
            category = CategoryEnum.OTHER
            logger.error("OpenAI API failed for categorization: %s", e, exc_info=True)

        # Step 5: Update the complaint with the classified category
        complaint.category = category  # type: ignore
        try:
            await self.session.commit()
            await self.session.refresh(complaint)
            logger.info(
                "Complaint category updated for id=%s: %s", complaint.id, category
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.critical("DB error during category update: %s", e, exc_info=True)
            raise

        # Step 6: Return the response schema
        return ComplaintResponse.from_orm(complaint)

    async def get_complaint_by_id(
        self, complaint_id: int
    ) -> Optional[ComplaintResponse]:
        """
        Retrieve a complaint by its unique identifier.

        Args:
            complaint_id (int): The unique ID of the complaint.

        Returns:
            Optional[ComplaintResponse]: The complaint record if found, else None.
        """
        logger.debug("Retrieving complaint by id=%s", complaint_id)
        complaint = await self.session.get(Complaint, complaint_id)
        if not complaint:
            logger.warning("Complaint not found: id=%s", complaint_id)
            return None
        logger.info("Complaint retrieved: id=%s", complaint_id)
        return ComplaintResponse.from_orm(complaint)

    async def get_complaints(
        self, status: Optional[StatusEnum] = None, since: Optional[datetime] = None
    ) -> List[ComplaintResponse]:
        """
        Retrieve complaints with optional filtering by status and timestamp.

        Args:
            status (Optional[StatusEnum]): Status to filter by.
            since (Optional[datetime]): Only complaints created after this timestamp.

        Returns:
            List[ComplaintResponse]: List of complaints.
        """
        logger.debug("Querying complaints (status=%s, since=%s)", status, since)
        query = select(Complaint)
        if status:
            query = query.where(Complaint.status == status)
        if since:
            query = query.where(Complaint.timestamp >= since)
        results = (await self.session.execute(query)).scalars().all()
        logger.info("Complaints queried, count=%d", len(results))
        return [ComplaintResponse.from_orm(c) for c in results]

    async def update_complaint_status(
        self, complaint_id: int, status: StatusEnum
    ) -> Optional[ComplaintResponse]:
        """
        Update the status of a complaint by its ID.

        Args:
            complaint_id (int): Complaint ID.
            status (StatusEnum): New status to set.

        Returns:
            Optional[ComplaintResponse]: The updated complaint if found, else None.
        """
        logger.debug("Updating status for complaint id=%s to %s", complaint_id, status)
        complaint = await self.session.get(Complaint, complaint_id)
        if not complaint:
            logger.warning("Complaint for update not found: id=%s", complaint_id)
            return None
        complaint.status = status  # type: ignore
        try:
            await self.session.commit()
            await self.session.refresh(complaint)
            logger.info("Complaint id=%s status updated to %s", complaint.id, status)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.critical(
                "DB error on status update id=%s: %s", complaint_id, e, exc_info=True
            )
            raise
        return ComplaintResponse.from_orm(complaint)
