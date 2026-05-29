from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from uuid import uuid4
import re

from database.db import get_connection, row_to_dict
from services.gradcam_service import create_gradcam_overlay
from services.model_service import predict_image
from services.report_service import generate_report


ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "uploads"


def handle_prediction(handler):
    content_type = handler.headers.get("Content-Type", "")
    match = re.search(r"boundary=(.+)", content_type)
    if not match:
        handler._json({"error": "Multipart form-data is required."}, status=400)
        return

    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length)
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body
    )

    fields = {}
    image_part = None
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        if filename:
            image_part = part
        elif name:
            fields[name] = part.get_content().strip()

    if image_part is None:
        handler._json({"error": "Please upload a chest X-ray image."}, status=400)
        return

    original_name = Path(image_part.get_filename()).name
    ext = Path(original_name).suffix.lower() or ".png"
    if ext not in {".jpg", ".jpeg", ".png"}:
        handler._json({"error": "Only JPG and PNG images are supported."}, status=400)
        return

    UPLOAD_DIR.mkdir(exist_ok=True)
    image_name = f"{uuid4().hex}{ext}"
    image_path = UPLOAD_DIR / image_name
    image_path.write_bytes(image_part.get_payload(decode=True))

    prediction = predict_image(image_path)
    gradcam_path = create_gradcam_overlay(image_path, prediction["prediction"])

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)",
            (
                fields.get("patientName") or "Anonymous Patient",
                _safe_int(fields.get("age")),
                fields.get("gender") or "Not specified",
            ),
        )
        patient_id = cursor.lastrowid
        cursor = conn.execute(
            """
            INSERT INTO predictions
            (patient_id, image_path, gradcam_path, prediction, confidence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                _public_path(image_path),
                _public_path(gradcam_path),
                prediction["prediction"],
                prediction["confidence"],
            ),
        )
        prediction_id = cursor.lastrowid
        conn.commit()
        report_path = generate_report(prediction_id)
        conn.execute(
            "UPDATE predictions SET report_path = ? WHERE id = ?",
            (_public_path(report_path), prediction_id),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT predictions.*, patients.name, patients.age, patients.gender
            FROM predictions
            JOIN patients ON patients.id = predictions.patient_id
            WHERE predictions.id = ?
            """,
            (prediction_id,),
        ).fetchone()

    handler._json({"result": row_to_dict(row)})


def _safe_int(value):
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def _public_path(path):
    return "/" + path.relative_to(ROOT).as_posix()
