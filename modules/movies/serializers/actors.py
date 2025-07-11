# movies/serializers/actors.py

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from movies.models import Actor
from modules.common.serializer import AuditableSerializerMixin


class ActorListSerializer(AuditableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = [
            'id', 'name', 'biography', 'birth_date',
            'created_date', 'created_by',
            'updated_date', 'updated_by',
            'deleted_date', 'deleted_by'
        ]


class ActorCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': _('El nombre del actor no puede estar vacío.'),
            'required': _('El nombre es obligatorio.')
        }
    )
    biography = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La biografía debe ser un texto válido.')
        }
    )
    birth_date = serializers.DateField(
        required=False,
        error_messages={
            'invalid': _('Fecha inválida.')
        }
    )

    class Meta:
        model = Actor
        fields = ['name', 'biography', 'birth_date']

    def validate_name(self, value):
        if Actor.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                _('Ya existe un actor con ese nombre.'))
        return value


class ActorUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages={
            'blank': _('El nombre no puede estar vacío.')
        }
    )
    biography = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La biografía debe ser un texto válido.')
        }
    )
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = Actor
        fields = ['name', 'biography', 'birth_date']
