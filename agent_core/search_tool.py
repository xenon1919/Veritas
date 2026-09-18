import logging

from ddgs import DDGS
from ddgs.exceptions import DDGSException

from .config import settings
from .exceptions import SearchError
from .retry import with_retry

logger = logging.getLogger(__name__)


@with_retry(attempts=3, base_delay=1.0, exceptions=(DDGSException,))
def _search(query: str, max_results: int):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def web_search(query: str, max_results: int = None) -> list[dict]:
    """Run a web search and return a list of {title, url, snippet} dicts."""
    max_results = max_results or settings.max_search_results
    logger.info("Searching: %r (max_results=%d)", query, max_results)

    try:
        raw_results = _search(query, max_results)
    except DDGSException as exc:
        logger.error("Search failed for %r: %s", query, exc)
        raise SearchError(f"Web search failed: {exc}") from exc

    results = [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in raw_results
    ]
    logger.info("Search returned %d results", len(results))
    return results
