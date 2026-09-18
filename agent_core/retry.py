import functools
import logging
import time

logger = logging.getLogger(__name__)


def with_retry(attempts: int = 3, base_delay: float = 1.0, exceptions=(Exception,)):
    """Retry a function with exponential backoff on the given exception types."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == attempts:
                        break
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                        fn.__name__, attempt, attempts, exc, delay,
                    )
                    time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator
