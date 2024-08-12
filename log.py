import sqlite3
from datetime import datetime

def log_event(event_type, user_id=None, details=""):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (event_type, user_id, details) VALUES (?, ?, ?)",
        (event_type, user_id, details)
    )
    conn.commit()
    conn.close()