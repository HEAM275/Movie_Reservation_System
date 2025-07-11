from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
import uuid


class AuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    access_token = models.TextField(unique=True)
    refresh_token = models.TextField(unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.expires_at

    @classmethod
    def get_active_token(cls, user):
        return cls.objects.filter(user=user, expires_at__gt=timezone.now()).first()

    def revoke(self):
        BlacklistedToken.objects.create(
            token=self.refresh_token, expires_at=self.expires_at
        )
        self.delete()


class BlacklistedToken(models.Model):
    token = models.TextField(unique=True)
    expires_at = models.DateTimeField()

    @classmethod
    def is_blacklisted(cls, token):
        return cls.objects.filter(token=token, expires_at__gt=timezone.now()).exists()


class EmailVerification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):

        return (timezone.now() - self.created_at).days < 1


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):

        return (timezone.now() - self.created_at).hours < 24
