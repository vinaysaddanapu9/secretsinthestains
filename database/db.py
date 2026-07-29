import os
import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

# Load .env only once
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create a connection pool
pool = ConnectionPool(DATABASE_URL)

def get_connection():
    return psycopg.connect(DATABASE_URL)






