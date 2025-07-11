from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import AuditableMixins


class MovieCategory(AuditableMixins):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Movie Category')
        verbose_name_plural = _('Movie Categories')

    def __str__(self):
        return self.name


class Actor(AuditableMixins):
    name = models.CharField(max_length=100, verbose_name=_('Full Name'))
    biography = models.TextField(blank=True, verbose_name=_('Biography'))
    birth_date = models.DateField(
        null=True, blank=True, verbose_name=_('Birth Date'))

    class Meta:
        verbose_name = _('Actor')
        verbose_name_plural = _('Actors')

    def __str__(self):
        return self.name


class Movie(AuditableMixins):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    release_date = models.DateField(verbose_name=_('Release Date'))
    categories = models.ManyToManyField(
        MovieCategory,
        related_name='movies',
        verbose_name=_('Categories')
    )
    cast = models.ManyToManyField(
        Actor,
        related_name='acted_in',
        verbose_name=_('Cast')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    class Meta:
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')
        ordering = ['-release_date']

    def __str__(self):
        return self.title
