import logging

from flask import Flask, Response, jsonify, render_template, request

import db
import jobs
from logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
db.init_db()


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
def index():
    return render_template("index.html")


@app.route("/history")
def history_page():
    return render_template("history.html")


@app.route("/report/<int:report_id>")
def report_page(report_id):
    return render_template("report.html", report_id=report_id)


@app.route("/api/research", methods=["POST"])
def api_start_research():
    body = request.get_json(silent=True) or {}
    question = body.get("question", "").strip()
    api_key = (body.get("api_key") or "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) > 500:
        return jsonify({"error": "question must be under 500 characters"}), 400
    if not api_key:
        return jsonify({"error": "A Gemini API key is required. Add yours in the field above."}), 400

    job_id = jobs.start_job(question, api_key=api_key)
    return jsonify({"job_id": job_id})


@app.route("/api/research/<job_id>/stream")
def api_stream_research(job_id):
    return Response(
        jobs.stream_job(job_id),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/history")
def api_history():
    return jsonify(db.list_reports())


@app.route("/api/report/<int:report_id>")
def api_report(report_id):
    report = db.get_report(report_id)
    if not report:
        return jsonify({"error": "not found"}), 404
    return jsonify(report)


@app.route("/api/stats")
def api_stats():
    return jsonify(db.get_stats())


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(500)
def server_error(err):
    logger.exception("Unhandled server error")
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
