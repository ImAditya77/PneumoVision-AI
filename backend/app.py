from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json
import mimetypes
import os
import traceback

from database.db import init_db
from routes.history import delete_history_item, get_history
from routes.predict import handle_prediction
from routes.reports import handle_report


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
STATIC_ROOT = FRONTEND
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))


class PneumoVisionHandler(BaseHTTPRequestHandler):
    server_version = "PneumoVisionAI/1.0"

    def do_GET(self):
        try:
            path = urlparse(self.path).path
            if path == "/api/history":
                self._json(get_history())
                return
            if path.startswith("/api/report/"):
                handle_report(self, path)
                return
            if path.startswith("/uploads/") or path.startswith("/reports/"):
                self._send_file(ROOT / path.lstrip("/"))
                return
            self._serve_frontend(path)
        except Exception as exc:
            self._error(exc)

    def do_POST(self):
        try:
            path = urlparse(self.path).path
            if path == "/api/predict":
                handle_prediction(self)
                return
            self._json({"error": "Not found"}, status=404)
        except Exception as exc:
            self._error(exc)

    def do_DELETE(self):
        try:
            path = urlparse(self.path).path
            if path.startswith("/api/history/"):
                prediction_id = int(path.rsplit("/", 1)[-1])
                self._json(delete_history_item(prediction_id))
                return
            self._json({"error": "Not found"}, status=404)
        except Exception as exc:
            self._error(exc)

    def _serve_frontend(self, path):
        if path in ("", "/"):
            file_path = FRONTEND / "index.html"
        else:
            file_path = STATIC_ROOT / path.lstrip("/")
        if not file_path.exists() or not file_path.is_file():
            file_path = FRONTEND / "index.html"
        self._send_file(file_path)

    def _send_file(self, file_path):
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload, status=200):
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, exc):
        traceback.print_exc()
        self._json({"error": str(exc)}, status=500)

    def log_message(self, format, *args):
        print("[%s] %s" % (self.log_date_time_string(), format % args))


def ensure_directories():
    for folder in ("uploads", "reports", "data", "model"):
        (ROOT / folder).mkdir(exist_ok=True)


def main():
    ensure_directories()
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), PneumoVisionHandler)
    print(f"PneumoVision AI running on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
