import os
import psycopg
from dotenv import load_dotenv
from psycopg.errors import UniqueViolation

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)


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