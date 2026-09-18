import pytest

from agent_core.retry import with_retry


def test_returns_result_on_success():
    @with_retry(attempts=3, base_delay=0)
    def fn():
        return "ok"

    assert fn() == "ok"


def test_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("agent_core.retry.time.sleep", lambda _: None)
    calls = {"n": 0}

    @with_retry(attempts=3, base_delay=0, exceptions=(ValueError,))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("boom")
        return "recovered"

    assert flaky() == "recovered"
    assert calls["n"] == 2


def test_raises_after_exhausting_attempts(monkeypatch):
    monkeypatch.setattr("agent_core.retry.time.sleep", lambda _: None)

    @with_retry(attempts=2, base_delay=0, exceptions=(ValueError,))
    def always_fails():
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fails()
