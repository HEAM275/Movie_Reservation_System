from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import ValidationError
from modules.common.serializer import AuditableSerializerMixin
from modules.cinema.models.screening_room import ScreeningRoom
from modules.cinema.models.cinema import Cinema


class ScreeningRoomListSerializer(AuditableSerializerMixin):
    class Meta:
        model = ScreeningRoom
        fields = ['cinema',
                'room_number',
                'capacity']
        
class ScreeningRoomCreateSerializer(AuditableSerializerMixin):
    cinema = serializers.PrimaryKeyRelatedField(
        queryset=Cinema.objects.all(),
        required=True,
        error_messages={
            'required': _('Cinema is required.'),
            'does_not_exist': _('Selected cinema does not exist.')
        }
    )
    room_number = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': _('Room number is required.'),
            'blank': _('Room number cannot be blank.')
        }
    )
    capacity = serializers.IntegerField(
        required=True,
        error_messages={
            'required': _('Capacity is required.'),
        }
    )

    class Meta:
        model = ScreeningRoom
        fields = ['cinema', 'room_number', 'capacity']

    def validate_cinema(self, value):
        if not value.is_active:
            raise ValidationError(_('Cinema is not active.'))
        return value

    def validate_room_number(self, value):
        cinema = self.initial_data.get('cinema')

        if cinema:
            if ScreeningRoom.objects.filter(cinema_id=cinema, room_number=value).exists():
                raise ValidationError(_('A room with this number already exists in the selected cinema.'))
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise ValidationError(_('Capacity must be greater than zero.'))
        return value

    def validate(self, data):
        cinema = data.get('cinema')
        capacity = data.get('capacity')

        if cinema and capacity:
            # Suma de capacidades actuales de ese cine (sin incluir esta sala si es update)
            used_capacity = ScreeningRoom.objects.filter(cinema=cinema).exclude(pk=self.instance.pk if self.instance else None).aggregate(
                total=serializers.Sum('capacity')
            )['total'] or 0

            if used_capacity + capacity > cinema.total_seats:
                remaining = cinema.total_seats - used_capacity
                raise ValidationError({
                    'capacity': _(f'The total capacity would exceed cinema limits. Only {remaining} seats are available.')
                })

        return data
    
class ScreeningRoomUpdateSerializer(AuditableSerializerMixin):
    cinema = serializers.PrimaryKeyRelatedField(
        queryset=Cinema.objects.all(),
        required=False,
        error_messages={
            'does_not_exist': _('Selected cinema does not exist.')
        }
    )
    room_number = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        error_messages={
            'blank': _('Room number cannot be blank.')
        }
    )
    capacity = serializers.IntegerField(
        required=False,
        error_messages={
            'min_value': _('Capacity must be greater than zero.')
        }
    )

    class Meta:
        model = ScreeningRoom
        fields = ['cinema', 'room_number', 'capacity']

    def validate_cinema(self, value):
        if value and not value.is_active:
            raise ValidationError(_('Cinema is not active.'))
        return value

    def validate_room_number(self, value):
        if not value:
            raise ValidationError(_('Room number cannot be blank.'))

        cinema = self.initial_data.get('cinema') or getattr(self.instance, 'cinema_id', None)

        if cinema:
            # Si ya existe y es la misma sala, permitir
            existing = ScreeningRoom.objects.filter(cinema_id=cinema, room_number=value).exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(_('A room with this number already exists in the selected cinema.'))
        return value

    def validate_capacity(self, value):
        if value is not None and value <= 0:
            raise ValidationError(_('Capacity must be greater than zero.'))
        return value

    def validate(self, data):
        cinema = data.get('cinema', getattr(self.instance, 'cinema', None))
        capacity = data.get('capacity', getattr(self.instance, 'capacity', None))

        if cinema and capacity is not None:
            used_capacity = ScreeningRoom.objects.filter(cinema=cinema).exclude(pk=self.instance.pk).aggregate(
                total=serializers.Sum('capacity')
            )['total'] or 0

            if used_capacity + capacity > cinema.total_seats:
                remaining = cinema.total_seats - used_capacity
                raise ValidationError({
                    'capacity': _(f'The total capacity would exceed cinema limits. Only {remaining} seats are available.')
                })

        return data

    def update(self, instance, validated_data):
        # Actualiza solo los campos proporcionados
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance