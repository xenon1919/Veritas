def test_save_and_get_report(tmp_db):
    report_id = tmp_db.save_report("What is Rust?", "Rust is a systems language.", [
        {"title": "Rust", "url": "https://rust-lang.org", "snippet": "..."}
    ], duration_seconds=1.5)

    saved = tmp_db.get_report(report_id)
    assert saved["question"] == "What is Rust?"
    assert saved["report"] == "Rust is a systems language."
    assert saved["sources"][0]["url"] == "https://rust-lang.org"
    assert saved["duration_seconds"] == 1.5


def test_get_report_missing_returns_none(tmp_db):
    assert tmp_db.get_report(999) is None


def test_list_reports_orders_newest_first(tmp_db):
    tmp_db.save_report("first", "r1", [])
    tmp_db.save_report("second", "r2", [])

    reports = tmp_db.list_reports()
    assert [r["question"] for r in reports] == ["second", "first"]


def test_stats_empty(tmp_db):
    stats = tmp_db.get_stats()
    assert stats == {"total_reports": 0, "avg_duration_seconds": 0}


def test_stats_with_reports(tmp_db):
    tmp_db.save_report("q1", "r1", [], duration_seconds=2.0)
    tmp_db.save_report("q2", "r2", [], duration_seconds=4.0)

    stats = tmp_db.get_stats()
    assert stats["total_reports"] == 2
    assert stats["avg_duration_seconds"] == 3.0
