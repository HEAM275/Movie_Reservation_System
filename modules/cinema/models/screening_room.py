from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.common.models import AuditableMixins
from modules.cinema.models.cinema import Cinema

class ScreeningRoom(AuditableMixins):
    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_number = models.PositiveIntegerField(_('Room Number'))
    capacity = models.PositiveIntegerField(_('Capacity'))

    def clean(self):
        # Evitar que se exceda la capacidad total del cine
        if self.cinema and self.capacity:
            current_capacity = ScreeningRoom.objects.filter(cinema=self.cinema).exclude(pk=self.pk).aggregate(
                total=models.Sum('capacity')
            )['total'] or 0

            if current_capacity + self.capacity > self.cinema.total_seats:
                remaining = self.cinema.total_seats - current_capacity
                raise ValidationError({
                    'capacity': _('La capacidad total de las salas no puede superar los %(total)d asientos del cine. Solo quedan %(remaining)d asientos disponibles.') % {
                        'total': self.cinema.total_seats,
                        'remaining': remaining
                    }
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Esto llama a clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cinema.name} - Room {self.room_number}"