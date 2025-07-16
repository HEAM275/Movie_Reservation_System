from rest_framework import serializers
from modules.services.models.showtime import Showtime
from modules.cinema.models.screening_room import ScreeningRoom
from modules.movies.models.movies import Movie
from django.utils.translation import gettext_lazy as _
from modules.common.serializer import AuditableSerializerMixin

class ShowtimeListSerializer(AuditableSerializerMixin):
    movie = serializers.CharField(source = 'movie.title')
    screening_room = serializers.StringRelatedField()

    class Meta:
        model = Showtime
        fields = [
            'id',
            'movie',
            'screening_room',
            'show_date',
            'available_seats',
            'is_full'
        ]

    def get_available_seats(self, obj):
        return obj.available_seats

    def get_is_full(self, obj):
        return obj.is_full
    

class ShowtimeCreateSerializer(AuditableSerializerMixin):
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        required=True,
        error_messages={"required": _("La película es obligatoria")}
    )
    screening_room = serializers.PrimaryKeyRelatedField(
        queryset=ScreeningRoom.objects.all(),
        required=True,
        error_messages={"required": _("La sala es obligatoria")}
    )
    show_date = serializers.DateTimeField(
        required=True,
        error_messages={"required": _("La fecha y hora son obligatorias")}
    )

    class Meta:
        model = Showtime
        fields = ['movie', 'screening_room', 'show_date']

    def validate(self, data):
        # Validar que la fecha no sea en el pasado
        from django.utils import timezone
        if data['show_date'] < timezone.now():
            raise serializers.ValidationError({
                'show_date': _('La fecha no puede ser en el pasado.')
            })

        # Validar que la sala pertenezca a un cine activo
        if not data['screening_room'].cinema.is_active:
            raise serializers.ValidationError({
                'screening_room': _('El cine no está activo.')
            })

        return data
    
class ShowtimeUpdateSerializer(AuditableSerializerMixin):
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        required=False
    )
    screening_room = serializers.PrimaryKeyRelatedField(
        queryset=ScreeningRoom.objects.all(),
        required=False
    )
    show_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Showtime
        fields = ['movie', 'screening_room', 'show_date']

    def validate(self, data):
        from django.utils import timezone

        if 'show_date' in data and data['show_date'] < timezone.now():
            raise serializers.ValidationError({
                'show_date': _('La fecha no puede ser en el pasado.')
            })

        if 'screening_room' in data and not data['screening_room'].cinema.is_active:
            raise serializers.ValidationError({
                'screening_room': _('El cine no está activo.')
            })

        return data