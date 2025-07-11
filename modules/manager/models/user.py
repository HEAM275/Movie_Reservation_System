# apps/manager/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from modules.common.models import AuditableMixins


class UserManager(BaseUserManager):
    """Gestor personalizado para el modelo User usando email como USERNAME_FIELD"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(
                _("The user most provide a correct email address"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("The superuser most have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("The superuser most have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, AuditableMixins):
    # Sobreescribimos username como opcional y lo dejamos solo para compatibilidad
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        null=True,
        help_text=_("Optional field"),
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _(" A user with that email already exists."),
        },
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"
