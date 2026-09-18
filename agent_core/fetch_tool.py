import logging

import requests
from bs4 import BeautifulSoup

from .config import settings
from .retry import with_retry

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}


@with_retry(attempts=2, base_delay=1.0, exceptions=(requests.RequestException,))
def _get(url: str) -> requests.Response:
    resp = requests.get(url, headers=HEADERS, timeout=settings.request_timeout)
    resp.raise_for_status()
    return resp


def fetch_page_text(url: str, max_chars: int = None) -> str:
    """Download a URL and return its main text content, truncated. Returns ""
    on any failure so callers can fall back to a search snippet."""
    max_chars = max_chars or settings.max_page_chars
    try:
        resp = _get(url)
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars]
