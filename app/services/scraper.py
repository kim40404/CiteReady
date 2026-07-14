"""Web content scraper for CiteReady.

Fetches raw HTML from URLs using httpx with proper error handling,
timeout management, and User-Agent headers to mimic a real browser.
"""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ScraperError(Exception):
    """Raised when scraping fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def fetch_url(url: str) -> str:
    """Fetch the raw HTML content of a URL.

    Args:
        url: The URL to fetch.

    Returns:
        The raw HTML string of the page.

    Raises:
        ScraperError: If the request fails for any reason.
    """
    headers = {
        "User-Agent": settings.SCRAPER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    logger.info("scraper.fetch_start", url=url, timeout=settings.SCRAPER_TIMEOUT)

    try:
        async with httpx.AsyncClient(
            timeout=settings.SCRAPER_TIMEOUT,
            follow_redirects=True,
            max_redirects=5,
        ) as client:
            response = await client.get(url, headers=headers)

        # Check for HTTP errors
        if response.status_code >= 400:
            logger.warning(
                "scraper.http_error",
                url=url,
                status_code=response.status_code,
            )
            raise ScraperError(
                f"HTTP {response.status_code}: Failed to fetch {url}",
                status_code=response.status_code,
            )

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            logger.warning(
                "scraper.non_html",
                url=url,
                content_type=content_type,
            )
            raise ScraperError(
                f"Non-HTML content type: {content_type}. CiteReady only analyzes HTML pages.",
            )

        html = response.text
        logger.info(
            "scraper.fetch_success",
            url=url,
            content_length=len(html),
            status_code=response.status_code,
        )
        return html

    except httpx.TimeoutException:
        logger.error("scraper.timeout", url=url, timeout=settings.SCRAPER_TIMEOUT)
        raise ScraperError(f"Timeout after {settings.SCRAPER_TIMEOUT}s fetching {url}")

    except httpx.ConnectError as e:
        logger.error("scraper.connect_error", url=url, error=str(e))
        raise ScraperError(f"Connection failed for {url}: {e}")

    except httpx.TooManyRedirects:
        logger.error("scraper.too_many_redirects", url=url)
        raise ScraperError(f"Too many redirects for {url}")

    except ScraperError:
        raise  # re-raise our own errors

    except Exception as e:
        logger.error("scraper.unexpected_error", url=url, error=str(e))
        raise ScraperError(f"Unexpected error fetching {url}: {e}")
