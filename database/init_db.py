import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    print("DATABASE_URL:", DATABASE_URL)
    return psycopg.connect(DATABASE_URL)

'''def get_connection():
    return psycopg.connect(DATABASE_URL)'''


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
            CREATE TABLE IF NOT EXISTS internships (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                college TEXT,
                domain TEXT,
                phone TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS webinar_registrations (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                gender TEXT NOT NULL,
                qualification TEXT NOT NULL,
                organization TEXT NOT NULL,
                department TEXT NOT NULL,
                city_state TEXT NOT NULL,
                question TEXT,
                consent BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Neon PostgreSQL database initialized successfully.")
