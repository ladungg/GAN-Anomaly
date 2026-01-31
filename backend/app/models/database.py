import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "anomaly_detection.db"

def get_db():
    """
    Kết nối tới SQLite database
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # truy cập theo tên cột
    # Enable autocommit - every statement is auto-committed
    # This ensures data is written immediately
    conn.isolation_level = None
    return conn
