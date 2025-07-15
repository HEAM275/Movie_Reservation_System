import django_filters
from modules.cinema.models.cinema import Cinema


class CinemaFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Cinema
        fields = ['name', 'is_active']