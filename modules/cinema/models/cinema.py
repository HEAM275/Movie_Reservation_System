from django.db import models
from django.utils.translation import gettext_lazy as _
from modules.common.models import AuditableMixins


class Cinema(AuditableMixins):
    name = models.CharField(_('Name'), max_length=255)
    address = models.TextField(_('Address'))
    total_seats = models.PositiveIntegerField(_('Total Seats'))
    is_active = models.BooleanField(verbose_name=_(u'Active'), default=True)

    def __str__(self):
        return self.name