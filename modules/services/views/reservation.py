from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from collections import defaultdict
from services.models.reservation import Reservation
from services.models.seat import Seat
from modules.manager.models import User
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            reservation = serializer.save()
            return Response(
                {"message": _("Reserva realizada exitosamente"), "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": _("Error al realizar la reserva"), "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance.user != request.user and not request.user.is_staff:
            raise PermissionDenied(_("No tienes permiso para editar esta reserva"))

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            updated_reservation = serializer.save()
            return Response(
                {"message": _("Reserva actualizada exitosamente"), "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": _("Error al actualizar la reserva"), "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.user != request.user and not request.user.is_staff:
                return Response({"detail": _("No tienes permiso para cancelar esta reserva")},
                                status=status.HTTP_403_FORBIDDEN)

            seat = instance.seat
            seat.is_reserved = False
            seat.save(update_fields=['is_reserved'])
            instance.delete()

            return Response(
                {"message": _("Reserva cancelada exitosamente")},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"message": _("Error al cancelar la reserva"), "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(operation_summary=_("Listar mis reservas"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Ver detalles de mi reserva"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Crear una nueva reserva"))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Actualizar una reserva"))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary=_("Cancelar una reserva"))
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# -----------------------------
# Serializadores
# -----------------------------


class ReservationListSerializer(serializers.ModelSerializer):
    seat = serializers.SerializerMethodField()
    showtime = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id', 'seat', 'showtime', 'reserved_at']

    def get_seat(self, obj):
        return f"{obj.seat.row}{obj.seat.number}"

    def get_showtime(self, obj):
        return {
            'id': obj.seat.showtime.id,
            'movie': obj.seat.showtime.movie.title,
            'show_date': obj.seat.showtime.show_date.strftime('%Y-%m-%d %H:%M')
        }


class ReservationCreateSerializer(serializers.ModelSerializer):
    showtime_id = serializers.PrimaryKeyRelatedField(
        queryset=Showtime.objects.all(),
        source='seat__showtime',
        error_messages={'does_not_exist': _('La función no existe o ya está llena.')}
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        required=False,
        error_messages={'min_value': _('La cantidad debe ser al menos 1.')}
    )

    class Meta:
        model = Reservation
        fields = ['showtime_id', 'quantity']

    def validate(self, data):
        showtime = data.get('seat__showtime')
        quantity = data.get('quantity', 1)

        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False).count()

        if available_seats == 0:
            raise serializers.ValidationError({'showtime_id': _('No hay asientos disponibles para esta función.')})

        if quantity > available_seats:
            raise serializers.ValidationError({
                'quantity': _(
                    'Solo hay %(available)d asientos disponibles. ¿Deseas reservar %(max)d?'
                ) % {'available': available_seats, 'max': available_seats}
            })

        # Guardar datos para usarlos en create()
        data['available_seats'] = available_seats
        return data

    def create(self, validated_data):
        showtime = validated_data['seat__showtime']
        quantity = validated_data.get('quantity', 1)

        available_seats = Seat.objects.filter(
            showtime=showtime, is_reserved=False
        )[:quantity]

        if not available_seats:
            raise serializers.ValidationError({'showtime_id': _('No hay asientos disponibles.')})

        user = validated_data['user']

        reservations = []
        for seat in available_seats:
            seat.is_reserved = True
            seat.save(update_fields=['is_reserved'])
            reservations.append(
                Reservation.objects.create(seat=seat, user=user)
            )

        return reservations[0] if len(reservations) == 1 else reservations


class ReservationUpdateSerializer(serializers.ModelSerializer):
    seat_id = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(),
        source='seat',
        required=True
    )

    class Meta:
        model = Reservation
        fields = ['seat_id']

    def validate(self, data):
        new_seat = data.get('seat')
        old_reservation = self.instance

        if new_seat.showtime != old_reservation.seat.showtime:
            raise serializers.ValidationError({'seat_id': _('El asiento debe ser de la misma función.')})

        if new_seat.is_reserved and new_seat.reservation_set.exists():
            raise serializers.ValidationError({'seat_id': _('Este asiento ya está reservado.')})

        return data

    def update(self, instance, validated_data):
        old_seat = instance.seat
        new_seat = validated_data.get('seat', instance.seat)

        if old_seat != new_seat:
            old_seat.is_reserved = False
            old_seat.save(update_fields=['is_reserved'])

            new_seat.is_reserved = True
            new_seat.save(update_fields=['is_reserved'])

        instance.seat = new_seat
        instance.save()
        return instance


# -----------------------------
# APIView para mapa de asientos
# -----------------------------


@swagger_auto_schema(tags=["Reservations"])
class SeatMapView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary=_("Mostrar mapa de asientos"),
        manual_parameters=[
            oa.Parameter('showtime_id', oa.IN_QUERY, description="ID de la función", type=oa.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        showtime_id = request.query_params.get('showtime_id')
        if not showtime_id:
            return Response({'error': _('showtime_id es requerido')}, status=400)

        try:
            showtime = Showtime.objects.get(id=showtime_id)
            seats = showtime.seats.all().order_by('row', 'number')

            grouped = defaultdict(list)
            for seat in seats:
                grouped[seat.row].append({
                    'number': seat.number,
                    'is_reserved': seat.is_reserved,
                    'id': seat.id
                })

            return Response(dict(grouped), status=200)
        except Showtime.DoesNotExist:
            return Response({'error': _('Función no encontrada')}, status=404)