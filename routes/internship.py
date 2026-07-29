from psycopg.errors import UniqueViolation
from database.db import get_connection

def get_all_applications():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM internships ORDER BY id DESC")
            return cur.fetchall()

def save_application(name, email, college, domain, phone):
    print("Application received")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO internships
                    (name, email, college, domain, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, email, college, domain, phone))

            conn.commit()

    except UniqueViolation:
        raise Exception("Mobile number already exists.")