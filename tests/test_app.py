import pytest


@pytest.fixture
def client(tmp_db, monkeypatch):
    import app as flask_app_module

    monkeypatch.setattr(flask_app_module.db, "DB_PATH", tmp_db.DB_PATH)
    flask_app_module.app.config["TESTING"] = True
    return flask_app_module.app.test_client()


def test_index_page(client):
    assert client.get("/").status_code == 200


def test_history_page(client):
    assert client.get("/history").status_code == 200


def test_health(client):
    assert client.get("/api/health").json == {"status": "ok"}


def test_research_requires_question(client):
    res = client.post("/api/research", json={})
    assert res.status_code == 400


def test_research_rejects_overlong_question(client):
    res = client.post("/api/research", json={"question": "x" * 501, "api_key": "k"})
    assert res.status_code == 400


def test_research_requires_api_key(client):
    res = client.post("/api/research", json={"question": "hello"})
    assert res.status_code == 400
    assert "API key" in res.json["error"]


def test_report_not_found(client):
    res = client.get("/api/report/9999")
    assert res.status_code == 404


def test_unknown_route_is_404(client):
    res = client.get("/nope")
    assert res.status_code == 404
