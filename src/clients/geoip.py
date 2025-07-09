"""
src/clients/geoip.py

Client for IP-based geolocation using a public API.
"""

import logging

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


async def get_geolocation(ip: str) -> dict:
    """
    Fetch geolocation information for the given IP address.

    Sends a GET request to the IP API
    endpoint configured in settings.ip_api_url.

    Args:
        ip: IP address to look up (e.g. "8.8.8.8").

    Returns:
        A dict with geolocation fields
        (country, regionName, city, lat, lon, etc.).

    Raises:
        httpx.HTTPError: on network or non-2xx response.
    """
    url = f"{settings.ip_api_url}/{ip}"
    logger.debug("GeoIP request: %s", url)
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info("GeoIP response for %s: %s", ip, data)
            return data
        except httpx.HTTPError as e:
            logger.error(
                "GeoIP lookup failed for %s: %s", ip, e, exc_info=True
            )  # noqa: E501
            raise
