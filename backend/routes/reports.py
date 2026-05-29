from pathlib import Path

from database.db import get_connection
from services.report_service import generate_report


ROOT = Path(__file__).resolve().parents[2]


def handle_report(handler, path):
    prediction_id = int(path.rsplit("/", 1)[-1])
    with get_connection() as conn:
        row = conn.execute(
            "SELECT report_path FROM predictions WHERE id = ?", (prediction_id,)
        ).fetchone()
    if row is None:
        handler._json({"error": "Report not found."}, status=404)
        return

    report_path = ROOT / row["report_path"].lstrip("/")
    if not report_path.exists():
        report_path = generate_report(prediction_id)
    data = report_path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/pdf")
    handler.send_header(
        "Content-Disposition", f'attachment; filename="pneumovision-report-{prediction_id}.pdf"'
    )
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)

