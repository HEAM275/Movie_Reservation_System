# movies/serializers/movie.py

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from modules.common.serializer import AuditableSerializerMixin
from modules.movies.models import Movie, Actor, MovieCategory


class MovieListSerializer(AuditableSerializerMixin, serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    cast = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'release_date',
            'categories', 'cast', 'is_active',
            'created_date', 'created_by',
            'updated_date', 'updated_by',
            'deleted_date', 'deleted_by',
        ]


class MovieCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=200,
        required=True,
        error_messages={
            'blank': _('El título no puede estar vacío.'),
            'required': _('El título es obligatorio.')
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La descripción debe ser un texto válido.')
        }
    )
    release_date = serializers.DateField(
        required=True,
        error_messages={
            'invalid': _('Fecha de lanzamiento inválida.'),
            'required': _('La fecha de lanzamiento es obligatoria.')
        }
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=MovieCategory.objects.all(),
        many=True
    )
    cast = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(),
        many=True
    )
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Movie
        fields = ['title', 'description', 'release_date',
                  'categories', 'cast', 'is_active']
        read_only_fields = [
            'created_date', 'created_by',
            'updated_date', 'updated_by',
            'deleted_date', 'deleted_by',
        ]

    def validate_title(self, value):
        if Movie.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                _('Ya existe una película con ese título.'))
        return value

    def validate_categories(self, value):
        category_ids = [category.id for category in value]
        existing_ids = list(MovieCategory.objects.filter(id__in=category_ids).values_list('id', flat=True))

        missing_ids = set(category_ids) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(
                _('Las siguientes categorías no existen: {}').format(', '.join(map(str, missing_ids)))
            )
        return value

    def validate_cast(self, value):
        actor_ids = [actor.id for actor in value]
        existing_ids = list(Actor.objects.filter(id__in=actor_ids).values_list('id', flat=True))

        missing_ids = set(actor_ids) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(
                _('Los siguientes actores no existen: {}').format(', '.join(map(str, missing_ids)))
            )
        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        cast = validated_data.pop('cast')

        movie = Movie.objects.create(**validated_data)
        movie.categories.set(categories)
        movie.cast.set(cast)
        return movie


class MovieUpdateSerializer(AuditableSerializerMixin, serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=200,
        required=False,
        error_messages={
            'blank': _('El título no puede estar vacío.'),
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': _('La descripción debe ser un texto válido.')
        }
    )
    release_date = serializers.DateField(
        required=False,
        error_messages={
            'invalid': _('Fecha inválida.'),
        }
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=MovieCategory.objects.all(),
        many=True,
        required=False
    )
    cast = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(),
        many=True,
        required=False
    )
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Movie
        fields = [
            'title', 'description', 'release_date',
            'categories', 'cast', 'is_active',
            # Campos de AuditableSerializerMixin:
            'created_date', 'created_by', 'updated_date', 'updated_by'
        ]
        read_only_fields = [
            'created_date', 'created_by',
            'updated_date', 'updated_by',
            'deleted_date', 'deleted_by',
        ]

    def validate_title(self, value):
        if value:
            movie_id = self.instance.id if self.instance else None
            if Movie.objects.filter(title=value).exclude(id=movie_id).exists():
                raise serializers.ValidationError(
                    _('Ya existe una película con ese título.'))
        return value

    def validate_categories(self, value):
        if value:
            category_ids = [category.id for category in value]
            existing_ids = list(MovieCategory.objects.filter(id__in=category_ids).values_list('id', flat=True))

            missing_ids = set(category_ids) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(
                    _('Las siguientes categorías no existen: {}').format(', '.join(map(str, missing_ids)))
                )
        return value

    def validate_cast(self, value):
        if value:
            actor_ids = [actor.id for actor in value]
            existing_ids = list(Actor.objects.filter(id__in=actor_ids).values_list('id', flat=True))

            missing_ids = set(actor_ids) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(
                    _('Los siguientes actores no existen: {}').format(', '.join(map(str, missing_ids)))
                )
        return value

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        cast = validated_data.pop('cast', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if categories is not None:
            instance.categories.set(categories)
        if cast is not None:
            instance.cast.set(cast)

        instance.save()
        return instance
