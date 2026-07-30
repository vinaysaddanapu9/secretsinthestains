from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf.csrf import CSRFProtect
from routes import internship
from routes.message import save_message, get_messages
from routes.webinar import webinar_bp,get_all_webinars, get_past_webinars, get_webinar_registrations
from werkzeug.security import generate_password_hash, check_password_hash
from routes.auth_utils import admin_required, login_required
from routes.certificate import certificate_bp
from reportlab.pdfgen import canvas
from scheduler import start_scheduler
from routes.quiz import quiz_bp
from dotenv import load_dotenv

load_dotenv()   # Loads DATABASE_URL from .env (ignored on Render)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("KanDukuri@98")

app = Flask(__name__)
app.secret_key = "SecretsInTheStains_AdminPanel_2026@SecureKey"

app.register_blueprint(quiz_bp)
app.register_blueprint(webinar_bp)
app.register_blueprint(certificate_bp)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

csrf = CSRFProtect(app)

from flask import send_from_directory

# Prevent browser cache
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

# ADMIN LOGIN (basic version)
@app.route('/admin-login', methods=['GET', 'POST'])
@login_required
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin'] = True
            session.permanent = True

            return redirect('/admin')
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")

# ADMIN DASHBOARD (protected)
@app.route('/admin')
@admin_required
@login_required
def admin():
    applications = internship.get_all_applications()
    messages = get_messages()
    webinar_registrations = get_webinar_registrations()

    webinar_success = request.args.get("webinar_success")

    return render_template(
        "admin.html",
        applications=applications,
        messages=messages,
        webinar_registrations=webinar_registrations,
        webinar_success=webinar_success
    )

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    session.pop('admin', None)
    return redirect('/admin-login')


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/programs")
def programs():
    return render_template("programs.html")

@app.route("/blogs")
def blogs():
    return render_template("blogs.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/internships')
def internships():
    success = request.args.get("success")
    error = request.args.get("error")
    return render_template(
        "internships.html",
        success=success,
        error=error
    )

@app.route('/submit-internship', methods=['POST'])
def submit_internship():
    name = request.form['name']
    email = request.form['email']
    college = request.form['college']
    domain = request.form['domain']
    phone = request.form['phone']

    try:
        internship.save_application(name, email, college, domain, phone)
        return redirect(url_for('internships', success=1))
    except Exception as e:
        return redirect(url_for('internships', error=str(e)))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        save_message(name, email, message)

        return redirect(url_for('contact', sent='1'))

    success = request.args.get('sent')
    return render_template("contact.html", success=success)

@app.route("/admin/webinars")
@login_required
@admin_required
def admin_webinars():
    webinars = get_all_webinars()
    return render_template(
        "/webinar/admin_webinars.html",
        webinars=webinars
    )

@app.route('/webinars')
def all_webinars():
    webinars = get_past_webinars()
    return render_template('/webinar/all_webinars.html', webinars=webinars)


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=5000, debug=True)
