from psycopg.errors import UniqueViolation
from database.db import get_connection
from routes.email_service import send_registration_email

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

            # Send email only after successful registration
            try:
                details = f"""
    College: {college}
    Domain: {domain}
    Phone: {phone}
    """

                send_registration_email(
                    to_email=email,
                    name=name,
                    registration_type="Internship",
                    title=domain,
                    details=details
                )

            except Exception as e:
                print("Email sending failed:", e)

    except UniqueViolation:
        raise Exception("Mobile number already exists.")