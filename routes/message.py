from database.db import get_connection

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