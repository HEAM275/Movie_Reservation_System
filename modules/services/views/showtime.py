from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from modules.services.models.showtime import Showtime
from modules.services.serializers.showtime import (
    ShowtimeListSerializer,
    ShowtimeCreateSerializer,
    ShowtimeUpdateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa
from django.utils import timezone


def get_user_fullname(user):
    if not user or not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username


@swagger_auto_schema(tags=["Showtimes"])
class ShowtimeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows showtimes to be viewed or edited.
    """
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return ShowtimeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShowtimeUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        request = self.request
        user = request.user

        if user.is_authenticated:
            full_name = get_user_fullname(user)
            serializer.save(
                created_by=full_name,
                created_date=timezone.now()
            )
        else:
            raise PermissionDenied(_("Usuario no autenticado"))

    def perform_update(self, serializer):
        request = self.request
        user = request.user

        if user.is_authenticated:
            full_name = get_user_fullname(user)
            serializer.save(
                updated_by=full_name,
                updated_date=timezone.now()
            )
        else:
            raise PermissionDenied(_("Usuario no autenticado"))

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

    @swagger_auto_schema(operation_summary=_("List all showtimes"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Retrieve a showtime by ID"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Create a new showtime"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"message": _("Función creada exitosamente"), "data": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(
            {"message": _("Error al crear la función"), "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(operation_summary=_("Update an existing showtime"))
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(
                {"message": _("Función actualizada exitosamente"), "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": _("Error al actualizar la función"), "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(operation_summary=_("Delete a showtime"))
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": _("Función eliminada exitosamente")},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"message": _("Error al eliminar la función"), "errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )