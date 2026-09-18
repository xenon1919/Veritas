import json
import logging
import queue
import threading
import uuid

import db
from agent_core.agent import research
from agent_core.exceptions import ResearchAgentError

logger = logging.getLogger(__name__)

_jobs = {}
_lock = threading.Lock()

DONE = "__done__"


def start_job(question: str, api_key: str = None) -> str:
    job_id = uuid.uuid4().hex
    q = queue.Queue()
    with _lock:
        _jobs[job_id] = q

    thread = threading.Thread(
        target=_run_job, args=(job_id, question, api_key, q), daemon=True
    )
    thread.start()
    return job_id


def _run_job(job_id: str, question: str, api_key: str, q: "queue.Queue"):
    logger.info("[job %s] started: %r", job_id, question)

    def on_progress(message: str):
        q.put({"type": "progress", "message": message})

    try:
        result = research(question, api_key=api_key, on_progress=on_progress)
        report_id = db.save_report(
            result["question"], result["report"], result["sources"], result["duration_seconds"]
        )
        logger.info("[job %s] completed, saved as report %d", job_id, report_id)
        q.put({"type": "result", "report_id": report_id, **result})
    except ResearchAgentError as exc:
        logger.error("[job %s] failed: %s", job_id, exc)
        q.put({"type": "error", "message": str(exc)})
    except Exception as exc:  # unexpected — still surfaced to the UI, not crashed silently
        logger.exception("[job %s] unexpected failure", job_id)
        q.put({"type": "error", "message": f"Unexpected error: {exc}"})
    finally:
        q.put(DONE)


def stream_job(job_id: str):
    """Generator yielding SSE-formatted events for a running job."""
    q = _jobs.get(job_id)
    if q is None:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Unknown or expired job'})}\n\n"
        return

    while True:
        item = q.get()
        if item == DONE:
            with _lock:
                _jobs.pop(job_id, None)
            break
        yield f"data: {json.dumps(item)}\n\n"
