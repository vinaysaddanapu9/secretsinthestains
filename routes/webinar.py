from flask import Blueprint, render_template, request, redirect, url_for
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

webinar_bp = Blueprint("webinar", __name__)

def get_connection():
    return psycopg.connect(DATABASE_URL)

@webinar_bp.route("/webinar", methods=["GET", "POST"])
def webinar():
    if request.method == "POST":
        save_webinar_registration(
            request.form["full_name"],
            request.form["email"],
            request.form["phone"],
            request.form["gender"],
            request.form["qualification"],
            request.form["organization"],
            request.form["department"],
            request.form["city_state"],
            request.form.get("question", ""),
            True if request.form.get("consent") else False
        )

        return redirect(url_for("webinar.success"))

    return render_template("webinar/webinar.html")


@webinar_bp.route("/webinar-success")
def success():
    return render_template("webinar_success.html")

def save_webinar_registration(
    full_name,
    email,
    phone,
    gender,
    qualification,
    organization,
    department,
    city_state,
    question,
    consent
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO webinar_registrations
                (full_name,email,phone,gender,qualification,
                 organization,department,city_state,question,consent)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                full_name,
                email,
                phone,
                gender,
                qualification,
                organization,
                department,
                city_state,
                question,
                consent
            ))
        conn.commit()