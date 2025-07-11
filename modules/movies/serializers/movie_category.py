# movies/serializers/movie_category.py

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from movies.models import MovieCategory
from modules.common.serializer import AuditableSerializerMixin


class MovieCategoryListSerializer(AuditableSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = MovieCategory
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_date', 'created_by',
            'updated_date', 'updated_by',
            'deleted_date', 'deleted_by'
        ]


class MovieCategoryCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': _('El nombre no puede estar vacío.'),
            'required': _('El nombre es obligatorio.')
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La descripción debe ser un texto válido.')
        }
    )
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = MovieCategory
        fields = ['name', 'description', 'is_active']

    def validate_name(self, value):
        if MovieCategory.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                _('Ya existe una categoría con ese nombre.'))
        return value


class MovieCategoryUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages={
            'blank': _('El nombre no puede estar vacío.')
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La descripción debe ser un texto válido.')
        }
    )
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = MovieCategory
        fields = ['name', 'description', 'is_active']
