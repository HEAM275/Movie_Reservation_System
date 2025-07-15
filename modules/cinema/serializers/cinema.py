# modules/cinema/serializers/cinema.py
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import ValidationError

from modules.common.serializer import AuditableSerializerMixin
from modules.cinema.models.cinema import Cinema



class CinemaListSerializer(AuditableSerializerMixin):
    class Meta:
        model = Cinema
        fields = ['id', 'name', 'address', 'total_seats', 'is_active']



class CinemaCreateSerializer(AuditableSerializerMixin):
    name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': _('Name is required.'),
            'blank': _('Name cannot be blank.')
        }
    )
    address = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': _('Address is required.'),
            'blank': _('Address cannot be blank.')
        }
    )
    total_seats = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages={
            'required': _('Total seats is required.'),
            'min_value': _('Total seats must be at least 1.')
        }
    )
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Cinema
        fields = ['name', 'address', 'total_seats', 'is_active']

    def validate_name(self, value):
        if Cinema.objects.filter(name=value).exists():
            raise ValidationError(_('A cinema with this name already exists.'))
        return value

    def validate_address(self, value):
        if not value.strip():
            raise ValidationError(_('Address cannot be empty or only spaces.'))
        return value

    def validate_total_seats(self, value):
        if value < 1:
            raise ValidationError(_('Total seats must be greater than zero.'))
        return value

    def create(self, validated_data):
        # Aseguramos que is_active tenga valor por defecto si no se envía
        validated_data.setdefault('is_active', True)
        return super().create(validated_data)
    
class CinemaUpdateSerializer(AuditableSerializerMixin):
    name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=False,
        error_messages={
            'blank': _('Name cannot be blank.')
        }
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True
    )
    total_seats = serializers.IntegerField(
        required=False,
        min_value=1,
        error_messages={
            'min_value': _('Total seats must be at least 1.')
        }
    )
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Cinema
        fields = ['name', 'address', 'total_seats', 'is_active']

    def validate_name(self, value):
        if value and Cinema.objects.filter(name=value).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('A cinema with this name already exists.'))
        return value

    def validate_address(self, value):
        if value and not value.strip():
            raise ValidationError(_('Address cannot be empty or only spaces.'))
        return value

    def validate_total_seats(self, value):
        if value is not None and value < 1:
            raise ValidationError(_('Total seats must be at least 1.'))
        return value

    def validate(self, data):
        # Si se actualiza el nombre, validar unicidad
        name = data.get('name')
        if name and Cinema.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError({
                'name': _('A cinema with this name already exists.')
            })
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance