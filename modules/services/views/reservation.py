from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from modules.services.models.reservation import Reservation,Seat
from modules.manager.models.user import User
from modules.services.serializers.reservation import  (
    ReservationListSerializer,
    ReservationCreateSerializer,
    ReservationUpdateSerializer
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa



def get_user_fullname(user):
    if not user or not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username


@swagger_auto_schema(tags=["Reservations"])
class ReservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to make or manage their own reservations.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReservationUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return Reservation.objects.filter(user=user)

    def perform_create(self, serializer):
        request = self.request
        user = request.user

        if user.is_authenticated:
            serializer.save(user=user)
        else:
            raise PermissionDenied(_("Usuario no autenticado"))
        

    @swagger_auto_schema(operation_summary=_("Listar mis reservas"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Ver detalles de mi reserva"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            reservation = serializer.save()
            return Response(
                {"message": "Reserva realizada exitosamente", "data": self.get_serializer(reservation).data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Error al realizar la reserva", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated = serializer.save()
            return Response(
                {"message": "Reserva actualizada exitosamente", "data": self.get_serializer(updated).data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Error al actualizar la reserva", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        reservations = group.reservations.all()
        if not reservations:
            return Response(
                {"message": "No hay asientos para liberar"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Liberar todos los asientos
        for reservation in reservations:
            seat = reservation.seat
            seat.is_reserved = False
            seat.save(update_fields=['is_reserved'])
            reservation.delete()

        group.delete()

        return Response(
            {"message": "Reserva cancelada exitosamente"},
            status=status.HTTP_204_NO_CONTENT
        )