# Veritas

Autonomous web research agent. Given a research question, searches the web, reads multiple sources in parallel, and
synthesizes a cited report using Gemini. Ships as a Flask web app with a live progress
pipeline, a history dashboard, retrying/fault-tolerant search & LLM calls, structured
logging, and a test suite — plus a CLI for quick one-off queries.

The web app is bring-your-own-key: each visitor pastes their own Gemini API key into the
UI (kept in `localStorage`, sent only with their own requests, never written to the
server or the database). That's what makes it safe to host publicly as a demo — no
server-side key means no way for visitors to burn your quota.

## Setup

```
pip install -r requirements-dev.txt   # or requirements.txt for runtime only
cp .env.example .env                  # optional — only needed for the CLI (see below)
```

## Run the web app

```
python app.py
```

Open http://127.0.0.1:5000 — that's the marketing landing page. Click "Launch App" (or go
straight to `/app`) to reach the research tool: paste a Gemini key (get one free at
[Google AI Studio](https://aistudio.google.com/apikey)), and submit a question. Watch the
live pipeline (search → read sources in parallel → synthesize), then read the cited
report with a clickable source list. Reports persist to `research.db` (SQLite) and are
browsable under "History", along with aggregate stats (total reports, average duration).
No `GEMINI_API_KEY` env var is required to run the server — it stays up even with zero
key configured, and requests without a key are rejected with a clear error.

## Run the CLI

The CLI is for your own local use, so it reads `GEMINI_API_KEY` from `.env` instead of
prompting for a key:

```
python main.py "What are the latest advances in solid-state batteries?"
```

## Run with Docker

```
docker build -t research-agent .
docker run -p 5000:5000 --env-file .env research-agent
```

## Run the tests

```
pytest
```

## Structure

```
agent_core/            research pipeline (importable package)
  config.py             typed Settings loaded from env, fails fast if misconfigured
  exceptions.py         SearchError / LLMError
  retry.py               exponential-backoff retry decorator
  search_tool.py          web search (DuckDuckGo), retried on failure
  fetch_tool.py            fetches and cleans page text, retried on failure
  llm.py                    Gemini wrapper (via LangChain), retried on failure
  agent.py                   orchestrates: search -> parallel fetch+summarize -> synthesize

db.py                  SQLite persistence for past reports + aggregate stats
jobs.py                 background job runner + SSE progress streaming
app.py                   Flask routes (pages + JSON/SSE API), error handlers
logging_config.py         structured console logging
templates/               server-rendered HTML (landing page + sidebar-shell app pages)
static/                   CSS/JS for the frontend (vanilla, no build step)
tests/                    pytest suite (db, retry, agent pipeline, Flask routes)
main.py                 CLI entry point
Dockerfile              gunicorn-based container image
```

## API

- `POST /api/research` `{question, api_key}` -> `{job_id}` (key is used for this request only, never persisted)
- `GET /api/research/<job_id>/stream` -> Server-Sent Events of progress + final result
- `GET /api/history` -> list of past reports
- `GET /api/report/<id>` -> a single saved report
- `GET /api/stats` -> total reports + average duration
- `GET /api/health` -> liveness check
