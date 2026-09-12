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

    # -----------------------------
    # Save application to database
    # -----------------------------
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO internships
                    (name, email, college, domain, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    name,
                    email,
                    college,
                    domain,
                    phone
                ))

            conn.commit()

        print("Internship application saved successfully")

    except UniqueViolation:
        raise Exception("Mobile number already exists.")

    # -----------------------------
    # Send confirmation email
    # -----------------------------
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

        print("Internship confirmation email sent")

    except Exception as e:
        print("Internship email sending failed:", e)

    return True


