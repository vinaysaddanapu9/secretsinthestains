import os
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    app.config["MAIL_SERVER"] = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("EMAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")
    app.config["MAIL_TIMEOUT"] = 10

    mail.init_app(app)


def send_registration_email(
    to_email,
    name,
    registration_type,
    title,
    details
):
    msg = Message(
        subject=f"{registration_type} Registration Confirmation - {title}",
        sender=os.getenv("EMAIL_USER"),
        recipients=[to_email]
    )

    msg.body = f"""
Hi {name},

Thank you for registering for the {registration_type}.

Registration Details
--------------------
{details}

Your registration has been successfully completed.

Regards,
Team
"""

    mail.send(msg)