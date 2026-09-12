import secrets
import io
import os
import qrcode
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from routes.auth_utils import admin_required
from database.db import get_connection
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from flask import current_app

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

@certificate_bp.route('/certificate/download/<certificate_id>')
def download_certificate(certificate_id):

    # -----------------------------------------
    # Get certificate from database
    # -----------------------------------------
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

    if not certificate:
        return "Certificate not found", 404

    # -----------------------------------------
    # Certificate data
    # -----------------------------------------
    certificate_id = certificate[0]
    name = certificate[1]
    program = certificate[2]
    issue_date = certificate[3]
    status = certificate[4]

    # -----------------------------------------
    # Create PDF
    # -----------------------------------------
    buffer = io.BytesIO()

    width, height = A4

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    # =========================================
    # COLORS
    # =========================================

    MAROON = colors.HexColor("#7F1D2D")
    DARK_MAROON = colors.HexColor("#5B1420")
    DARK = colors.HexColor("#111827")
    GRAY = colors.HexColor("#6B7280")
    LIGHT_GRAY = colors.HexColor("#E5E7EB")
    CREAM = colors.HexColor("#F8F5EF")

    # =========================================
    # BACKGROUND
    # =========================================

    pdf.setFillColor(CREAM)

    pdf.rect(
        0,
        0,
        width,
        height,
        fill=1,
        stroke=0
    )

    # =========================================
    # MAROON OUTER BORDER
    # =========================================

    pdf.setStrokeColor(MAROON)
    pdf.setLineWidth(2.5)

    pdf.rect(
        10 * mm,
        10 * mm,
        width - 20 * mm,
        height - 20 * mm,
        fill=0,
        stroke=1
    )

    # =========================================
    # MAROON INNER BORDER
    # =========================================

    pdf.setStrokeColor(DARK_MAROON)
    pdf.setLineWidth(0.8)

    pdf.rect(
        15 * mm,
        15 * mm,
        width - 30 * mm,
        height - 30 * mm,
        fill=0,
        stroke=1
    )

    # =========================================
    # BRAND / LOGO AREA
    # =========================================

    logo_path = os.path.join(
        current_app.root_path,
        "static",
        "images",
        "logo.jpg"
    )

    logo_width = 35 * mm
    logo_height = 20 * mm

    pdf.drawImage(
        ImageReader(logo_path),
        (width - logo_width) / 2,
        height - 37 * mm,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask="auto"
    )

    # Brand name
    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 48 * mm,
        "SECRETS IN THE STAINS"
    )

    # Subtitle
    pdf.setFillColor(GRAY)

    pdf.setFont(
        "Helvetica",
        7.5
    )

    pdf.drawCentredString(
        width / 2,
        height - 54 * mm,
        "FORENSIC LEARNING & CERTIFICATION"
    )

    # =========================================
    # MAROON DIVIDER
    # =========================================

    pdf.setStrokeColor(MAROON)
    pdf.setLineWidth(1.2)

    pdf.line(
        28 * mm,
        height - 62 * mm,
        width - 28 * mm,
        height - 62 * mm
    )

    # =========================================
    # OFFICIAL CERTIFICATE
    # =========================================

    pdf.setFillColor(MAROON)

    pdf.setFont(
        "Helvetica-Bold",
        8
    )

    pdf.drawCentredString(
        width / 2,
        height - 73 * mm,
        "OFFICIAL CERTIFICATE"
    )

    # =========================================
    # CERTIFICATE TITLE
    # =========================================

    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        27
    )

    pdf.drawCentredString(
        width / 2,
        height - 88 * mm,
        "CERTIFICATE"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.setFillColor(GRAY)

    pdf.drawCentredString(
        width / 2,
        height - 97 * mm,
        "OF COMPLETION"
    )

    # =========================================
    # PRESENTED TO
    # =========================================

    pdf.setFont(
        "Helvetica",
        8.5
    )

    pdf.setFillColor(GRAY)

    pdf.drawCentredString(
        width / 2,
        height - 115 * mm,
        "THIS CERTIFICATE IS PRESENTED TO"
    )

    # =========================================
    # STUDENT NAME
    # =========================================

    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        23
    )

    pdf.drawCentredString(
        width / 2,
        height - 128 * mm,
        name.upper()
    )

    # Maroon underline

    name_width = pdf.stringWidth(
        name.upper(),
        "Helvetica-Bold",
        23
    )

    pdf.setStrokeColor(MAROON)
    pdf.setLineWidth(1)

    pdf.line(
        (width - name_width) / 2,
        height - 132 * mm,
        (width + name_width) / 2,
        height - 132 * mm
    )

    # =========================================
    # PROGRAM
    # =========================================

    pdf.setFillColor(GRAY)

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        width / 2,
        height - 144 * mm,
        "for successfully completing"
    )

    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawCentredString(
        width / 2,
        height - 154 * mm,
        program
    )

    # =========================================
    # INFORMATION BOX
    # =========================================

    box_x = 25 * mm
    box_y = height - 190 * mm
    box_width = width - 50 * mm
    box_height = 26 * mm

    pdf.setFillColor(colors.HexColor("#EEE9E3"))

    pdf.roundRect(
        box_x,
        box_y,
        box_width,
        box_height,
        3 * mm,
        fill=1,
        stroke=0
    )

    # Top maroon line

    pdf.setFillColor(MAROON)

    pdf.rect(
        box_x,
        box_y + box_height - 1.2 * mm,
        box_width,
        1.2 * mm,
        fill=1,
        stroke=0
    )

    # Labels

    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        7
    )

    pdf.drawString(
        32 * mm,
        box_y + 17 * mm,
        "CERTIFICATE ID"
    )

    pdf.drawString(
        32 * mm,
        box_y + 8 * mm,
        "ISSUE DATE"
    )

    pdf.drawString(
        105 * mm,
        box_y + 17 * mm,
        "STATUS"
    )

    # Values

    pdf.setFont(
        "Helvetica",
        8
    )

    pdf.drawString(
        65 * mm,
        box_y + 17 * mm,
        certificate_id
    )

    if hasattr(issue_date, "strftime"):
        formatted_date = issue_date.strftime("%d %B %Y")
    else:
        formatted_date = str(issue_date)

    pdf.drawString(
        65 * mm,
        box_y + 8 * mm,
        formatted_date
    )

    # Status

    pdf.setFillColor(colors.HexColor("#166534"))

    pdf.setFont(
        "Helvetica-Bold",
        8
    )

    pdf.drawString(
        125 * mm,
        box_y + 17 * mm,
        str(status).upper()
    )

    # =========================================
    # QR CODE
    # =========================================

    verification_url = url_for(
        "certificate.verify_certificate",
        certificate_id=certificate_id,
        _external=True
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=5,
        border=2
    )

    qr.add_data(verification_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    qr_buffer = io.BytesIO()

    qr_image.save(
        qr_buffer,
        format="PNG"
    )

    qr_buffer.seek(0)

    qr_reader = ImageReader(qr_buffer)

    pdf.drawImage(
        qr_reader,
        width - 65 * mm,
        39 * mm,
        width=30 * mm,
        height=30 * mm,
        preserveAspectRatio=True,
        mask="auto"
    )

    # =========================================
    # DIGITAL VERIFICATION
    # =========================================

    pdf.setFillColor(MAROON)

    pdf.setFont(
        "Helvetica-Bold",
        8
    )

    pdf.drawString(
        25 * mm,
        54 * mm,
        "DIGITAL VERIFICATION"
    )

    pdf.setFillColor(GRAY)

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.drawString(
        25 * mm,
        48 * mm,
        "Scan the QR code to verify"
    )

    pdf.drawString(
        25 * mm,
        43 * mm,
        "this certificate online."
    )

    # =========================================
    # FOUNDERS
    # =========================================

    # Founder line
    pdf.setStrokeColor(MAROON)
    pdf.setLineWidth(0.8)

    pdf.line(
        25 * mm,
        32 * mm,
        72 * mm,
        32 * mm
    )

    pdf.line(
        92 * mm,
        32 * mm,
        139 * mm,
        32 * mm
    )

    # Founder names

    pdf.setFillColor(DARK)

    pdf.setFont(
        "Helvetica-Bold",
        7
    )

    pdf.drawCentredString(
        48.5 * mm,
        26 * mm,
        "SAI SUDHA KANDUKURI"
    )

    pdf.drawCentredString(
        115.5 * mm,
        26 * mm,
        "M. VIJAYKRISHNA"
    )

    # Titles

    pdf.setFillColor(GRAY)

    pdf.setFont(
        "Helvetica",
        6.5
    )

    pdf.drawCentredString(
        48.5 * mm,
        22 * mm,
        "FOUNDER"
    )

    pdf.drawCentredString(
        115.5 * mm,
        22 * mm,
        "CO-FOUNDER"
    )

    # =========================================
    # FOOTER
    # =========================================

    pdf.setFillColor(GRAY)

    pdf.setFont(
        "Helvetica",
        6
    )

    pdf.drawCentredString(
        width / 2,
        16 * mm,
        f"Verification Reference: {certificate_id}"
    )

    # =========================================
    # SAVE
    # =========================================

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{certificate_id}.pdf"
    )