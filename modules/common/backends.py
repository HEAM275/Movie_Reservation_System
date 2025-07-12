from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailAdminAuthBackend(ModelBackend):
    """
    Backend para permitir login en el admin usando email y contraseña.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

        return None
