from agent_core import agent


def test_research_no_results(monkeypatch):
    monkeypatch.setattr(agent, "web_search", lambda question, max_results=None: [])

    result = agent.research("nothing findable")
    assert result["sources"] == []
    assert "No search results" in result["report"]


def test_research_happy_path(monkeypatch):
    fake_results = [
        {"title": "A", "url": "https://a.com", "snippet": "snippet a"},
        {"title": "B", "url": "https://b.com", "snippet": "snippet b"},
    ]
    monkeypatch.setattr(agent, "web_search", lambda question, max_results=None: fake_results)
    monkeypatch.setattr(agent, "fetch_page_text", lambda url: f"content for {url}")
    monkeypatch.setattr(
        agent.llm, "ask",
        lambda prompt, api_key=None: "SUMMARY" if "Page content" in prompt else "FINAL REPORT",
    )

    progress_messages = []
    result = agent.research("test question", on_progress=progress_messages.append)

    assert result["question"] == "test question"
    assert result["report"] == "FINAL REPORT"
    assert result["sources"] == fake_results
    assert result["duration_seconds"] >= 0
    assert any("Searching" in m for m in progress_messages)
    assert any("Done" in m for m in progress_messages)


def test_research_handles_summarize_failure(monkeypatch):
    from agent_core.exceptions import LLMError

    fake_results = [
        {"title": "A", "url": "https://a.com", "snippet": "snippet a"},
        {"title": "B", "url": "https://b.com", "snippet": "snippet b"},
    ]
    monkeypatch.setattr(agent, "web_search", lambda question, max_results=None: fake_results)
    monkeypatch.setattr(agent, "fetch_page_text", lambda url: "content")

    def ask(prompt, api_key=None):
        if "source [1]" in prompt:
            raise LLMError("gemini down for source a")
        if "Page content" in prompt:
            return "SUMMARY B"
        return "FINAL REPORT"

    monkeypatch.setattr(agent.llm, "ask", ask)

    result = agent.research("q")
    assert result["report"] == "FINAL REPORT"
