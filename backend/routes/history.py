from database.db import get_connection, row_to_dict


def get_history():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT predictions.*, patients.name, patients.age, patients.gender
            FROM predictions
            JOIN patients ON patients.id = predictions.patient_id
            ORDER BY predictions.created_at DESC, predictions.id DESC
            """
        ).fetchall()
    records = [row_to_dict(row) for row in rows]
    pneumonia = sum(1 for row in records if row["prediction"] == "Pneumonia")
    normal = sum(1 for row in records if row["prediction"] == "Normal")
    avg_confidence = round(
        sum(row["confidence"] for row in records) / len(records), 2
    ) if records else 0
    return {
        "records": records,
        "stats": {
            "total": len(records),
            "normal": normal,
            "pneumonia": pneumonia,
            "averageConfidence": avg_confidence,
        },
    }


def delete_history_item(prediction_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT patient_id FROM predictions WHERE id = ?", (prediction_id,)
        ).fetchone()
        if row is None:
            return {"deleted": False}
        conn.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        conn.execute("DELETE FROM patients WHERE id = ?", (row["patient_id"],))
    return {"deleted": True}

