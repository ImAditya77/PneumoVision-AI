from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "pneumovision.db"


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                gradcam_path TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                report_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            """
        )


def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

