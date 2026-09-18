import logging
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import settings
from .exceptions import LLMError
from .retry import with_retry

logger = logging.getLogger(__name__)


@lru_cache(maxsize=64)
def _client_for(api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=api_key,
        temperature=0.2,
    )


@with_retry(attempts=3, base_delay=2.0, exceptions=(Exception,))
def _invoke(prompt: str, api_key: str) -> str:
    return _client_for(api_key).invoke(prompt).content


def ask(prompt: str, api_key: str = None) -> str:
    """Send a prompt to Gemini and return the text response.

    api_key defaults to the server's GEMINI_API_KEY (CLI/local use). The web
    app always passes the caller's own key explicitly.
    """
    api_key = api_key or settings.gemini_api_key
    if not api_key:
        raise LLMError("No Gemini API key provided.")

    try:
        return _invoke(prompt, api_key)
    except Exception as exc:
        logger.error("Gemini call failed: %s", exc)
        raise LLMError(f"Gemini call failed: {exc}") from exc
