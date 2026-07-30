from flask import Blueprint, render_template, request, redirect, url_for
from routes.auth_utils import admin_required,login_required
from datetime import date
from database.db import get_connection

webinar_bp = Blueprint("webinar", __name__)

@webinar_bp.route("/webinar")
def webinar():
    update_expired_webinars()

    # This is required for popup
    success = request.args.get("success")

    webinars = get_active_webinars()
    return render_template(
        "webinar/webinar.html",
        webinars=webinars,
        success = success
    )

@webinar_bp.route("/webinar-registration", methods=["POST"])
def webinar_registration():

    consent = "consent" in request.form

    webinar_id = request.form["webinar_id"]
    save_webinar_registration(
        webinar_id,
        request.form["full_name"],
        request.form["email"],
        request.form["phone"],
        request.form["gender"],
        request.form["qualification"],
        request.form["organization"],
        request.form["department"],
        request.form["city_state"],
        request.form.get("question", ""),
        consent
    )

    return redirect(url_for("webinar.webinar", success=1))

@webinar_bp.route("/admin/create-webinar", methods=["POST"])
@admin_required
@login_required
def create_webinar():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO webinars
                (
                    title,
                    speaker,
                    description,
                    webinar_date,
                    webinar_time,
                    duration,
                    platform,
                    meeting_link,
                    status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                request.form["title"],
                request.form["speaker"],
                request.form.get("description", ""),
                request.form["webinar_date"],
                request.form["webinar_time"],
                request.form.get("duration", ""),
                request.form.get("platform", "Google Meet"),
                request.form.get("meeting_link", ""),
                "Active"
            ))

        conn.commit()

    return redirect(url_for("admin", webinar_success=1))

@webinar_bp.route("/webinar-success")
def success():
    return render_template("webinar_success.html")

def save_webinar_registration(
    webinar_id,
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
                (
                    webinar_id,
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
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                webinar_id,
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

def get_active_webinars():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT *
                FROM webinars
                WHERE status='Active'
                ORDER BY webinar_date ASC
            """)

            return cur.fetchall()

def update_expired_webinars():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE webinars
                SET status = 'Expired'
                WHERE webinar_date < CURRENT_DATE
                  AND status = 'Active'
            """)
        conn.commit()

def get_all_webinars():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT *
                FROM webinars
                ORDER BY webinar_date DESC, webinar_time DESC
            """)

            return cur.fetchall()

def get_past_webinars():
    today = date.today()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    speaker,
                    description,
                    webinar_date,
                    webinar_time,
                    meeting_link
                FROM webinars
                WHERE webinar_date < %s
                ORDER BY webinar_date DESC, webinar_time DESC
            """, (today,))

            return cur.fetchall()

@webinar_bp.route("/admin/delete-webinar/<int:webinar_id>")
@admin_required
def delete_webinar(webinar_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Delete registrations first (important because of foreign key)
            cur.execute(
                "DELETE FROM webinar_registrations WHERE webinar_id = %s",
                (webinar_id,)
            )

            # Delete webinar
            cur.execute(
                "DELETE FROM webinars WHERE id = %s",
                (webinar_id,)
            )

        conn.commit()

    return redirect(url_for("webinar.admin_webinars", deleted=1))

def get_webinar_registrations():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    wr.id,
                    w.title,
                    wr.full_name,
                    wr.email,
                    wr.phone,
                    wr.created_at
                FROM webinar_registrations wr
                JOIN webinars w
                    ON wr.webinar_id = w.id
                ORDER BY wr.created_at DESC
            """)
            return cur.fetchall()