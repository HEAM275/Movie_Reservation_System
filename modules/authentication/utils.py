import jwt
import uuid
from django.conf import settings
from django.utils.timezone import now, timedelta

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_access_token(user):
    payload = {
        "user_id": str(user.id),
        "exp": now() + timedelta(minutes=15),
        "iat": now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token():
    return str(uuid.uuid4())


# apps/authentication/utils.py


def send_verification_email(user, token):
    subject = "Confirma tu correo electrónico"
    verification_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"

    html_message = render_to_string(
        "emails/verify_email.html", {"user": user,
                                     "verification_url": verification_url}
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )


def send_password_reset_email(user, token):
    subject = "Restablece tu contraseña"
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={token}"

    html_message = render_to_string(
        "emails/reset_password.html", {"user": user, "reset_url": reset_url}
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )
