import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import llm
from .config import settings
from .exceptions import LLMError
from .fetch_tool import fetch_page_text
from .search_tool import web_search

logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = """You are researching the question: "{question}"

Below is the content of a web page (source [{n}]: {url}).
Extract only the facts relevant to the question, as concise bullet points.
If the page has nothing relevant, reply with "No relevant information."

Page content:
{content}
"""

SYNTHESIZE_PROMPT = """You are a research assistant. Using ONLY the numbered source notes below,
write a well-organized, cited report answering the question: "{question}"

Cite sources inline using [n] matching the source numbers. End with a "Sources" list
mapping each [n] to its URL.

Source notes:
{notes}
"""


def _noop(*args, **kwargs):
    pass


def _summarize_source(question: str, index: int, result: dict, api_key: str) -> str:
    content = fetch_page_text(result["url"])
    if not content:
        content = result["snippet"]

    summary = llm.ask(
        SUMMARIZE_PROMPT.format(
            question=question, n=index, url=result["url"], content=content
        ),
        api_key=api_key,
    )
    return f"[{index}] {result['url']}\n{summary}"


def research(question: str, api_key: str = None, max_results: int = None, on_progress=None) -> dict:
    """Run the research pipeline: search -> read+summarize sources in parallel ->
    synthesize a cited report. api_key is the caller's Gemini key (falls back to
    the server's GEMINI_API_KEY for CLI/local use). on_progress(str) receives
    human-readable status updates. Returns {question, report, sources, duration_seconds}."""
    on_progress = on_progress or _noop
    if not (api_key or settings.gemini_api_key):
        raise LLMError("No Gemini API key provided.")

    started = time.monotonic()

    on_progress(f"Searching the web for: {question}")
    results = web_search(question, max_results=max_results)
    if not results:
        on_progress("No search results found.")
        return {"question": question, "report": "No search results found.", "sources": [], "duration_seconds": 0}

    on_progress(f"Found {len(results)} sources. Reading and summarizing (in parallel)...")

    notes = [None] * len(results)
    with ThreadPoolExecutor(max_workers=settings.max_parallel_fetches) as pool:
        future_to_index = {
            pool.submit(_summarize_source, question, i, result, api_key): i
            for i, result in enumerate(results, start=1)
        }
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            url = results[i - 1]["url"]
            try:
                notes[i - 1] = future.result()
                on_progress(f"[{i}/{len(results)}] Summarized {url}")
            except LLMError as exc:
                logger.warning("Failed to summarize source %d (%s): %s", i, url, exc)
                notes[i - 1] = f"[{i}] {url}\nNo relevant information (fetch/summarize failed)."
                on_progress(f"[{i}/{len(results)}] Failed to summarize {url}, skipping")

    on_progress("Synthesizing final report...")
    report = llm.ask(
        SYNTHESIZE_PROMPT.format(question=question, notes="\n\n".join(notes)),
        api_key=api_key,
    )

    duration = round(time.monotonic() - started, 1)
    on_progress(f"Done in {duration}s.")
    return {
        "question": question,
        "report": report,
        "sources": results,
        "duration_seconds": duration,
    }
