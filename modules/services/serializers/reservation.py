from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from modules.services.models.reservation import Reservation , Seat
from modules.services.models.showtime import Showtime
from modules.manager.models.user import User


class ReservationListSerializer(serializers.ModelSerializer):
    seat = serializers.SerializerMethodField()
    showtime = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'seat', 'showtime', 'reserved_at']

    def get_seat(self, obj):
        return f"{obj.seat.row}{obj.seat.number}"

    def get_showtime(self, obj):
        return obj.seat.showtime.id
    
class ReservationCreateSerializer(serializers.ModelSerializer):
    showtime_id = serializers.PrimaryKeyRelatedField(
        queryset=Showtime.objects.all(),
        source='seat__showtime',
        error_messages={'does_not_exist': _('La función no existe o ya está llena.')}
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        error_messages={
            'min_value': _('La cantidad debe ser al menos 1.')
        }
    )

    class Meta:
        model = Reservation
        fields = ['user', 'showtime_id', 'quantity']

    def validate(self, data):
        showtime = data.get('seat__showtime')
        quantity = data.get('quantity', 1)

        # Validar que el showtime exista
        if not showtime:
            raise serializers.ValidationError({'showtime_id': _('La función no existe.')})

        # Validar que haya suficientes asientos
        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False).count()
        if available_seats == 0:
            raise serializers.ValidationError({'showtime_id': _('No hay asientos disponibles para esta función.')})

        if quantity > available_seats:
            raise serializers.ValidationError({
                'quantity': _(
                    'Solo hay %(available)d asientos disponibles. ¿Deseas reservar %(max)d?'
                ) % {'available': available_seats, 'max': available_seats}
            })

        data['quantity'] = min(data.get('quantity', 1), available_seats)
        return data

    def create(self, validated_data):
        showtime = validated_data['seat__showtime']
        quantity = validated_data.get('quantity', 1)

        # Obtener los asientos disponibles
        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False)[:quantity]
        if not available_seats:
            raise serializers.ValidationError({'showtime_id': _('No hay asientos disponibles para esta función.')})

        if available_seats.count() < quantity:
            raise serializers.ValidationError({
                'quantity': _(
                    'Solo hay %(available)d asientos disponibles. ¿Deseas reservar %(max)d?'
                ) % {'available': available_seats.count(), 'max': available_seats.count()}
            })

        # Marcar los asientos como reservados
        user = validated_data['user']
        reservations = []
        for seat in available_seats:
            seat.is_reserved = True
            seat.save(update_fields=['is_reserved'])
            reservations.append(Reservation.objects.create(user=user, seat=seat))

        return reservations

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
        seat = data.get('seat')
        if seat.is_reserved and seat.reservation_set.exists():
            raise serializers.ValidationError({'seat_id': _('Este asiento ya está reservado.')})
        return data

    def update(self, instance, validated_data):
        seat = validated_data.get('seat')
        if seat.is_reserved:
            raise serializers.ValidationError({'seat_id': _('Este asiento ya está reservado.')})

        # Liberar el asiento actual
        instance.seat.is_reserved = False
        instance.seat.save(update_fields=['is_reserved'])

        # Asignar nuevo asiento
        seat.is_reserved = True
        seat.save(update_fields=['is_reserved'])

        instance.seat = seat
        instance.save()
        return instance