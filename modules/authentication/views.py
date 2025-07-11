import jwt
from django.conf import settings
from modules.manager.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from .utils import (
    generate_access_token,
    generate_refresh_token,
    send_verification_email,
    send_password_reset_email,
)
from .models import AuthToken, BlacklistedToken, EmailVerification, PasswordResetToken
from django.utils import timezone
from datetime import timedelta

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


login_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING, description="Correo del usuario"
        ),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING, description="Contraseña del usuario"
        ),
    },
    required=["email", "password"],
)

login_responses = {
    200: openapi.Response(
        "Tokens generados",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    ),
    400: openapi.Response("Error en credenciales"),
}


@swagger_auto_schema(request_body=login_request_body, responses=login_responses)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            # Revocar cualquier sesión activa
            active_token = AuthToken.get_active_token(user)
            if active_token:
                active_token.revoke()

            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token()
            expires_at = timezone.now() + timedelta(days=7)

            AuthToken.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )

            return Response(
                {"access_token": access_token, "refresh_token": refresh_token},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


refresh_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "refresh_token": openapi.Schema(
            type=openapi.TYPE_STRING, description="Token de refresco"
        )
    },
    required=["refresh_token"],
)

refresh_responses = {
    200: openapi.Response(
        "Nuevo token generado",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    ),
    401: openapi.Response("Token inválido o revocado"),
}


@swagger_auto_schema(request_body=refresh_request_body, responses=refresh_responses)
class RefreshTokenView(APIView):
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]

            if BlacklistedToken.is_blacklisted(refresh_token):
                return Response(
                    {"error": "Refresh token revocado"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            token_obj = AuthToken.objects.filter(
                refresh_token=refresh_token).first()
            if not token_obj or not token_obj.is_valid():
                return Response(
                    {"error": "Refresh token inválido o expirado"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            new_access_token = generate_access_token(token_obj.user)
            new_refresh_token = generate_refresh_token()
            new_expires_at = timezone.now() + timedelta(days=7)

            token_obj.revoke()
            AuthToken.objects.create(
                user=token_obj.user,
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_at=new_expires_at,
            )

            return Response(
                {"access_token": new_access_token,
                    "refresh_token": new_refresh_token},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logout_responses = {
    200: openapi.Response("Sesión cerrada correctamente"),
    400: openapi.Response("Token no proporcionado"),
    401: openapi.Response("Token inválido o expirado"),
}


@swagger_auto_schema(
    operation_description="Cierra sesión y revoca el token actual",
    responses=logout_responses,
)
class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                {"error": "Token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST
            )

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            token_obj = AuthToken.objects.filter(
                access_token=token, user=user).first()
            if token_obj:
                token_obj.revoke()

            return Response(
                {"detail": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


register_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING, description="Correo electrónico"
        ),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING, description="Contraseña del usuario"
        ),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=["email", "password"],
)

register_responses = {
    201: openapi.Response("Registro exitoso. Revisa tu correo."),
    400: openapi.Response("Datos inválidos"),
}


@swagger_auto_schema(
    operation_description="Registra un nuevo usuario y envía correo de verificación",
    request_body=register_request_body,
    responses=register_responses,
)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # verification, created = EmailVerification.objects.get_or_create(user=user)
            # send_verification_email(user, verification.token)

            return Response(
                {"detail": "Registro exitoso. Revisa tu correo."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


verify_email_parameters = [
    openapi.Parameter(
        "token",
        openapi.IN_QUERY,
        description="Token de verificación",
        type=openapi.TYPE_STRING,
    )
]

verify_email_responses = {
    200: openapi.Response("Correo verificado correctamente"),
    400: openapi.Response("Token inválido o expirado"),
}


@swagger_auto_schema(
    manual_parameters=verify_email_parameters, responses=verify_email_responses
)
class VerifyEmailView(APIView):
    def get(self, request):
        serializer = VerifyEmailSerializer(data=request.query_params)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            verification = EmailVerification.objects.filter(
                token=token).first()

            if not verification or not verification.is_valid():
                return Response(
                    {"error": "Token inválido o expirado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            verification.is_verified = True
            verification.save()
            verification.user.is_active = True
            verification.user.save()

            return Response(
                {"detail": "Correo verificado correctamente"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


forgot_password_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING, description="Correo del usuario"
        )
    },
    required=["email"],
)

forgot_password_responses = {
    200: openapi.Response("Se ha enviado un enlace a tu correo."),
    404: openapi.Response("Usuario no encontrado"),
}


@swagger_auto_schema(
    request_body=forgot_password_request_body, responses=forgot_password_responses
)
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                reset_token, created = PasswordResetToken.objects.get_or_create(
                    user=user
                )
                send_password_reset_email(user, reset_token.token)
                return Response(
                    {"detail": "Se ha enviado un enlace a tu correo."},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


reset_password_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "password": openapi.Schema(type=openapi.TYPE_STRING),
        "token": openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=["password", "token"],
)

reset_password_responses = {
    200: openapi.Response("Contraseña actualizada correctamente"),
    400: openapi.Response("Token inválido o contraseña incorrecta"),
}


@swagger_auto_schema(
    request_body=reset_password_request_body, responses=reset_password_responses
)
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            reset_obj = PasswordResetToken.objects.filter(token=token).first()

            if not reset_obj or not reset_obj.is_valid():
                return Response(
                    {"error": "Token inválido o expirado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = reset_obj.user
            user.set_password(password)
            user.save()

            reset_obj.delete()

            return Response(
                {"detail": "Contraseña actualizada correctamente."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
