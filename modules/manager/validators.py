from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


def validate_password_strength(password, username):
    if len(password) < 8:
        raise ValidationError(_("Password must be less than 8 characters"))
    if username.lower() in password.lower():
        raise ValidationError(_("Password must not contain username"))


def validate_email_address(email):
    try:
        validate_email(email)
    except:
        raise ValidationError(
            _(
                "The email address is not valid make sure it is in the format of email@domain.com"
            )
        )
