import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_all_applications():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM internships ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()
    return data

def backup_db():
    try:
        backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        backup_name = os.path.join(
            backup_dir,
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )

        shutil.copy(DB_PATH, backup_name)
        print("Backup created:", backup_name)

    except Exception as e:
        print("Backup failed:", e)


def save_message(name, email, message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages (name, email, message)
        VALUES (?, ?, ?)
    """, (name, email, message))

    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM messages ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()
    return data