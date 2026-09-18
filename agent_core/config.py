import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    max_search_results: int
    max_page_chars: int
    max_parallel_fetches: int
    request_timeout: int


def load_settings() -> Settings:
    # No server-side key is required: the web app accepts a per-request key
    # from the caller (see agent_core.llm), so a public demo never burns the
    # operator's own quota. GEMINI_API_KEY here is only a fallback for the
    # CLI (main.py) and local development.
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        max_search_results=_env_int("MAX_SEARCH_RESULTS", 5),
        max_page_chars=_env_int("MAX_PAGE_CHARS", 6000),
        max_parallel_fetches=_env_int("MAX_PARALLEL_FETCHES", 4),
        request_timeout=_env_int("REQUEST_TIMEOUT", 10),
    )


settings = load_settings()
