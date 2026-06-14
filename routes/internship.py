import sqlite3
import os

DB_PATH = os.path.join("database", "database.db")

def save_application(name, email, college, domain, phone):
    print("Application received")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO internships (name, email, college, domain, phone)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, college, domain, phone))

    conn.commit()
    conn.close()