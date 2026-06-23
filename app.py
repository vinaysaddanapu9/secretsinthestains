from flask import Flask, render_template, request, redirect, session, url_for,make_response
from routes import internship, quiz
from database.db import get_all_applications, save_message, backup_db, get_messages
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from reportlab.pdfgen import canvas
from io import BytesIO
from routes.quiz import quiz_bp

#backup_db()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("KanDukuri@98")

app = Flask(__name__)
app.secret_key = "SecretsInTheStains_AdminPanel_2026@SecureKey"

app.register_blueprint(quiz_bp)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

from flask import send_from_directory

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

# ADMIN LOGIN (basic version)
@app.route('/admin-login', methods=['GET', 'POST'])
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

# ADMIN DASHBOARD (protected)
@app.route('/admin')
@admin_required
def admin():
    applications = get_all_applications()
    messages = get_messages()

    return render_template(
        "admin.html",
        applications=applications,
        messages=messages
    )

# LOGOUT
@app.route('/logout')
def logout():
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


@app.route("/certificate-verification")
def certificate_verification():
    return render_template("verify_certificate.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/internships')
def internships():
    return render_template('internships.html')

@app.route('/submit-internship', methods=['POST'])
def submit_internship():
    name = request.form['name']
    email = request.form['email']
    college = request.form['college']
    domain = request.form['domain']
    phone = request.form['phone']

    internship.save_application(name, email, college, domain, phone)

    return "Application submitted successfully"

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)