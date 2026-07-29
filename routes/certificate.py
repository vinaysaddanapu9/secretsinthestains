from flask import Blueprint, render_template, request, redirect, url_for
from routes.auth_utils import admin_required
from database.db import get_connection
import secrets

certificate_bp = Blueprint('certificate', __name__)

# ------------------------------------------------
# Verify certificate using URL
# Example: /verify/CERT-2026-00001
# ------------------------------------------------
@certificate_bp.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    certificate_id,
                    name,
                    program,
                    issue_date,
                    status
                FROM certificates
                WHERE certificate_id = %s
            """, (certificate_id,))

            certificate = cur.fetchone()

    return render_template(
        'certificates/verify_certificate.html',
        certificate=certificate
    )

# ------------------------------------------------
# Certificate verification search page
# ------------------------------------------------
@certificate_bp.route('/certificate-verification', methods=['GET', 'POST'])
def certificate_verification_page():

    certificate = None

    if request.method == 'POST':

        certificate_id = request.form.get('certificate_id')

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        certificate_id,
                        name,
                        program,
                        issue_date,
                        status
                    FROM certificates
                    WHERE certificate_id = %s
                """, (certificate_id,))

                certificate = cur.fetchone()

    return render_template(
        'certificates/verify_certificate.html',
        certificate=certificate
    )

def generate_certificate_id():
    return f"SITS-{secrets.token_hex(4).upper()}"

# -------------------------------
# Admin - Certificate Management
# -------------------------------
@certificate_bp.route('/admin/certificates')
@admin_required
def admin_certificates():

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    certificate_id,
                    name,
                    program,
                    issue_date,
                    status
                FROM certificates
                ORDER BY issue_date DESC
            """)

            certificates = cur.fetchall()

    return render_template(
        'certificates/admin_certificates.html',
        certificates=certificates
    )

# -------------------------------
# Admin - Create Certificate
# -------------------------------
@certificate_bp.route('/admin/certificates/create', methods=['POST'])
@admin_required
def create_certificate():

    name = request.form.get('name')
    program = request.form.get('program')

    certificate_id = generate_certificate_id()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO certificates
                (certificate_id, name, program)
                VALUES (%s, %s, %s)
            """, (certificate_id, name, program))

        conn.commit()

    return redirect(url_for('certificate.admin_certificates'))