from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status


def get_user_fullname(user):
    if not user or not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username


class BaseModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        request = self.request
        user = request.user

        if user.is_authenticated:
            full_name = get_user_fullname(user)
            serializer.save(created_by=full_name, created_date=timezone.now())
        else:
            raise PermissionDenied("Usuario no autenticado")

    def perform_update(self, serializer):
        request = self.request
        user = request.user

        if user.is_authenticated:
            full_name = get_user_fullname(user)
            serializer.save(updated_by=full_name, updated_date=timezone.now())
        else:
            raise PermissionDenied("Usuario no autenticado")

    def perform_destroy(self, instance):
        request = self.request
        user = request.user

        if user.is_authenticated:
            full_name = get_user_fullname(user)
            instance.deleted_by = full_name
            instance.deleted_date = timezone.now()
            instance.is_active = False
            instance.save()
        else:
            instance.deleted_by = "Desconocido"
            instance.deleted_date = timezone.now()
            instance.is_active = False
            instance.save()
