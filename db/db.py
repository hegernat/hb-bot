import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "hb.sqlite"
print("USING DATABASE:", DB_PATH)

_connection = None


def get_db():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row
    return _connection


def init_db():
    db = get_db()
    schema_path = BASE_DIR / "db" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()