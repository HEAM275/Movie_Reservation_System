from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from modules.services.models.showtime import Showtime
from modules.cinema.models.screening_room import ScreeningRoom
from modules.movies.models.movies import Movie
from django.utils.translation import gettext_lazy as _
from modules.common.serializer import AuditableSerializerMixin

class ShowtimeListSerializer(AuditableSerializerMixin):
    movie = serializers.CharField(source = 'movie.title')
    screening_room = serializers.StringRelatedField()
    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
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
        show_date = data.get('show_date')
        if show_date and show_date < timezone.now():
            raise ValidationError({'show_date': _('La fecha no puede ser en el pasado.')})

        # Validar que el cine esté activo
        screening_room = data.get('screening_room')
        if screening_room and not screening_room.cinema.is_active:
            raise ValidationError({'screening_room': _('El cine no está activo.')})

        # Validar que no haya otra función en la misma sala en las próximas 3 horas
        if show_date and screening_room:
            min_gap = show_date - timezone.timedelta(hours=3)
            max_gap = show_date + timezone.timedelta(hours=3)

            conflicting = Showtime.objects.filter(
                screening_room=screening_room,
                show_date__range=(min_gap, max_gap)
            ).exclude(is_active=False)

            if conflicting.exists():
                suggested = (show_date + timezone.timedelta(hours=3)).isoformat()
                raise ValidationError({
                    'show_date': _(
                        'Ya hay una función programada cerca de esta hora. '
                        'Por favor, programa tu función al menos 3 horas después. '
                        'Sugerencia: %(suggested)s'
                    ) % {'suggested': suggested}
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

        show_date = data.get('show_date')
        screening_room = data.get('screening_room')

        # Validar que la fecha no sea en el pasado
        if show_date and show_date < timezone.now():
            raise ValidationError({'show_date': _('La fecha no puede ser en el pasado.')})

        # Validar que el cine esté activo
        if screening_room and not screening_room.cinema.is_active:
            raise ValidationError({'screening_room': _('El cine no está activo.')})

        # Validar que no haya otra función en la misma sala en las próximas 3 horas
        if show_date and screening_room:
            min_gap = show_date - timezone.timedelta(hours=3)
            max_gap = show_date + timezone.timedelta(hours=3)

            conflicting = Showtime.objects.filter(
                screening_room=screening_room,
                show_date__range=(min_gap, max_gap)
            ).exclude(pk=self.instance.pk if self.instance else None)

            if conflicting.exists():
                suggested = (show_date + timezone.timedelta(hours=3)).isoformat()
                raise ValidationError({
                    'show_date': _(
                        'Ya hay una función programada cerca de esta hora. '
                        'Por favor, programa tu función al menos 3 horas después. '
                        'Sugerencia: %(suggested)s'
                    ) % {'suggested': suggested}
                })

        return data