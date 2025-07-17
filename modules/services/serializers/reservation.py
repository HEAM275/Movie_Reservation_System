from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from modules.services.models.showtime import Showtime
from modules.services.models.reservation import Reservation, ReservationGroup,Seat
from modules.manager.models import User


class ReservationListSerializer(serializers.ModelSerializer):
    showtime = serializers.SerializerMethodField()
    seats = serializers.SerializerMethodField()

    class Meta:
        model = ReservationGroup
        fields = ['id', 'showtime', 'seats', 'created_at']

    def get_showtime(self, obj):
        return {
            'id': obj.showtime.id,
            'movie': obj.showtime.movie.title,
            'show_date': obj.showtime.show_date.strftime('%Y-%m-%d %H:%M')
        }

    def get_seats(self, obj):
        return list(obj.reservations.values_list('seat__row', 'seat__number'))

class ReservationCreateSerializer(serializers.ModelSerializer):
    showtime_id = serializers.PrimaryKeyRelatedField(
        queryset=Showtime.objects.all(),
        source='seat__showtime',
        error_messages={'does_not_exist': _('La función no existe o ya está llena.')}
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=20,
        default=1,
        required=False,
        error_messages={
            'min_value': _('La cantidad debe ser al menos 1.'),
            'max_value': _('No puedes reservar más de 20 asientos.')
        }
    )

    class Meta:
        model = Reservation
        fields = ['showtime_id', 'quantity']

    def validate(self, data):
        showtime = data.get('seat__showtime')
        quantity = data.get('quantity', 1)

        # Obtener asientos disponibles
        available_seats = Seat.objects.filter(is_reserved=False, showtime=showtime).count()
        if available_seats == 0:
            raise serializers.ValidationError({'showtime_id': _('No hay asientos disponibles para esta función.')})

        if quantity > available_seats:
            raise serializers.ValidationError({
                'quantity': _(
                    'Solo hay %(available)d asientos disponibles. ¿Deseas reservar %(available)d?'
                ) % {'available': available_seats}
            })

        data['available_seats'] = Seat.objects.filter(is_reserved=False, showtime=showtime)[:quantity]
        return data

    def create(self, validated_data):
        available_seats = validated_data.pop('available_seats')
        user = self.context['request'].user

        # Crear o obtener el grupo de reservas
        group, created = ReservationGroup.objects.get_or_create(
            user=user,
            showtime=validated_data['seat__showtime']
        )

        # Crear las reservas individuales
        for seat in available_seats:
            Reservation.objects.create(group=group, seat=seat)

        return group
    

class ReservationUpdateSerializer(serializers.ModelSerializer):
    showtime_id = serializers.PrimaryKeyRelatedField(
        queryset=Showtime.objects.all(),
        source='seat__showtime'
    )
    add_quantity = serializers.IntegerField(
        min_value=1,
        default=1,
        required=False
    )

    class Meta:
        model = Reservation
        fields = ['showtime_id', 'add_quantity']

    def validate(self, data):
        group = self.instance  # ReservationGroup
        showtime = data.get('seat__showtime') or group.showtime
        quantity = data.get('add_quantity', 1)

        available_seats = Seat.objects.filter(showtime=showtime, is_reserved=False).count()
        existing_seats = group.reservations.count()

        if quantity > available_seats:
            raise serializers.ValidationError({
                'add_quantity': _(
                    'Solo hay %(available)d asientos disponibles. ¿Deseas agregar %(available)d?'
                ) % {'available': available_seats}
            })

        data['showtime'] = showtime
        data['available_seats'] = Seat.objects.filter(
            showtime=showtime, is_reserved=False
        )[:quantity]

        return data

    def update(self, instance, validated_data):
        available_seats = validated_data['available_seats']
        showtime = validated_data['showtime']

        for seat in available_seats:
            Reservation.objects.create(group=instance, seat=seat)

        return instance