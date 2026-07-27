import os
import psycopg
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL)


def get_all_applications():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM internships ORDER BY id DESC")
            return cur.fetchall()


def save_message(name, email, message):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (name, email, message)
                VALUES (%s, %s, %s)
            """, (name, email, message))
        conn.commit()


def get_messages():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM messages ORDER BY id DESC")
            return cur.fetchall()


def get_webinar_registrations():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    full_name,
                    email,
                    phone,
                    gender,
                    qualification,
                    organization,
                    department,
                    city_state,
                    question,
                    created_at
                FROM webinar_registrations
                ORDER BY created_at DESC
            """)

            return cur.fetchall()

