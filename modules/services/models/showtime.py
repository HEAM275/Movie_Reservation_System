from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.cinema.models.screening_room import ScreeningRoom
from modules.movies.models.movies import Movie
from modules.common.models import AuditableMixins


class Showtime(AuditableMixins):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        verbose_name=_("Movie")
    )
    screening_room = models.ForeignKey(
        ScreeningRoom,
        on_delete=models.CASCADE,
        verbose_name=_("Screening Room")
    )
    show_date = models.DateTimeField(_("Show Date and Time"))

    def __str__(self):
        return f"{self.movie.title} - {self.show_date}"

    @property
    def available_seats(self):
        from modules.services.models.reservation import Reservation
        # Filtramos las reservas donde seat pertenezca a este showtime
        reserved = Reservation.objects.filter(seat__showtime=self).count()
        return self.screening_room.capacity - reserved

    @property
    def is_full(self):
        return self.available_seats <= 0