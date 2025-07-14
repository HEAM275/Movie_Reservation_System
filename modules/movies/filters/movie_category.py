from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.validators import ValidationError
from modules.movies.models.movies import *


class MovieCategoryFilter(filters.FilterSet):
    
    id = filters.NumberFilter(field_name='id', lookup_expr='exact',method="filter_by_id")
    name = filters.CharFilter(field_name='name', lookup_expr='icontains',method= "filter_by_name")
    description = filters.CharFilter( field_name='description', lookup_expr='icontains',method='filter_by_description')
    is_active = filters.BooleanFilter(field_name='is_active', lookup_expr='exact')

    class Meta:
        model = MovieCategory
        fields = {
            'id': ['exact'],
            'name': ['exact', 'contains'],
            'description': ['exact', 'contains'],
            'is_active' : ['exact']
            }
        
    def filter_by_id(self, queryset, name, value):
        if value is None:
            raise ValidationError(_("ID cannot be null"))
        try:
            value = int(value)
        except ValueError:
                raise ValidationError(_("ID must be an integer"))
        if not MovieCategory.objects.filter(id=value):
            raise ValidationError(_("MovieCategory with ID {} does not exist".format(value)))
        else:
            return queryset.filter(id=value)
    
    def filter_by_name(self, queryset, name, value):
        if value is None:
            raise ValidationError(_("Name cannot be null"))
        value = value.strip()
        if not queryset.filter(name__icontains=value).exists():
            raise ValidationError(_("Name {} does not exist".format(value)))
        return queryset.filter(name__icontains=value)
    
    def filter_by_description( self, queryset, name, value):
        if value is None:
            raise ValidationError(_("Description cannot be null"))
        value = value.strip()
        if not queryset.filter(description__icontains=value).exists():
            raise ValidationError(_("Description {} does not exist".format(value)))
        else:
            return queryset.filter(description__icontains=value)