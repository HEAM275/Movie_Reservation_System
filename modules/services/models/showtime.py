from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.cinema.models.screening_room import ScreeningRoom
from modules.movies.models.movies import Movie
from modules.common.models import AuditableMixins


class Showtime(AuditableMixins):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screening_room = models.ForeignKey(
        ScreeningRoom,
        on_delete=models.CASCADE,
        related_name='showtimes'
    )
    show_date = models.DateTimeField(_("Show Date and Time"))
    is_active = models.BooleanField(default=True)


    @property
    def available_seats(self):
        from modules.services.models.reservation import Reservation
        reserved = Reservation.objects.filter(seat__showtime=self).count()
        return self.screening_room.capacity - reserved

    @property
    def is_full(self):
        return self.available_seats <= 0

    def __str__(self):
        return f"{self.movie.title} - {self.show_date}"

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if creating:
            self._create_seats()

    def _create_seats(self):
        from modules.services.models.reservation import Seat
        rows = ['A', 'B', 'C']  # Puedes usar más filas si quieres
        capacity = self.screening_room.capacity
        per_row = capacity // len(rows)

        for row in rows:
            for number in range(1, per_row + 1):
                Seat.objects.create(
                    showtime=self,
                    row=row,
                    number=number
                )