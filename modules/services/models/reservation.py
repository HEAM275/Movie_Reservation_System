from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.manager.models import User
from modules.services.models.showtime import Showtime


class Seat(models.Model):
    showtime = models.ForeignKey(
        Showtime,
        on_delete=models.CASCADE,
        related_name='seats'
    )
    row = models.CharField(_('Row'), max_length=5)
    number = models.PositiveIntegerField(_('Number'))
    is_reserved = models.BooleanField(_('Is Reserved'), default=False)

    class Meta:
        unique_together = ('showtime', 'row', 'number')

    def __str__(self):
        return f"{self.row}{self.number} - {self.showtime}"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.seat}"