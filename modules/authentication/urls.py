# apps/authentication/urls.py

from django.urls import path
from modules.authentication.views import LoginView, RefreshTokenView, LogoutView
from modules.authentication.views import (
    RegisterView,
    VerifyEmailView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    # Iniciar sesión
    path("login/", LoginView.as_view(), name="auth-login"),
    # Refrescar token de acceso
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    # Cerrar sesión
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    # Registrarse
    path("register/", RegisterView.as_view(), name="auth-register"),
    # email para verificar
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    #
    path("forgot-password/", ForgotPasswordView.as_view(),
         name="auth-forgot-password"),
    # Resetear contrasena
    path(
        "reset-password/<str:token>/",
        ResetPasswordView.as_view(),
        name="auth-reset-password",
    ),
]
