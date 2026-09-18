import os

# agent_core.config reads GEMINI_API_KEY at import time, so this must be set
# before any test module imports agent_core.
os.environ.setdefault("GEMINI_API_KEY", "test-key")

import pytest


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    import db

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))
    db.init_db()
    return db
