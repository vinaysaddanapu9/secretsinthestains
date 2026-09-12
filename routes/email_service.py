import os
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

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
        sender=mail.app.config["MAIL_USERNAME"],
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
Sai Sudha Kandukuri
Founder SITS
"""

    mail.send(msg)