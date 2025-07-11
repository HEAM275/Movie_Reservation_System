import django_filters
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from movies.models import Movie, MovieCategory, Actor


class CustomValidationAPIError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error de validación.'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class MovieFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains'
    )
    release_date = django_filters.DateFilter(
        field_name='release_date', lookup_expr='exact'
    )
    categories = django_filters.ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=MovieCategory.objects.all(),
        conjoined=True
    )
    cast = django_filters.ModelMultipleChoiceFilter(
        field_name='cast',
        queryset=Actor.objects.all(),
        conjoined=True
    )

    class Meta:
        model = Movie
        fields = ['title', 'release_date', 'categories', 'cast']

    def filter_queryset(self, queryset):
        data = self.data

        # Validación del título
        title = data.get('title')
        if title is not None:
            title = title.strip()
            if not title:
                raise CustomValidationAPIError({
                    "title": ["El título no puede estar vacío si se proporciona."]
                })

            queryset = queryset.filter(title__icontains=title)
            if not queryset.exists():
                raise CustomValidationAPIError({
                    "title": [f"No se encontró ninguna película con el título '{title}'."]
                })

        # Validación de la fecha
        release_date = data.get('release_date')
        if release_date:
            try:
                from datetime import datetime
                datetime.strptime(release_date, '%Y-%m-%d')
            except ValueError:
                raise CustomValidationAPIError({
                    "release_date": ["Fecha inválida. Use el formato YYYY-MM-DD."]
                })

            queryset = queryset.filter(release_date=release_date)
            if not queryset.exists():
                raise CustomValidationAPIError({
                    "release_date": [f"No se encontró ninguna película lanzada el {release_date}."]
                })

        # Validación de categorías
        category_ids = data.getlist('categories')
        if category_ids:
            try:
                category_ids = [int(cid) for cid in category_ids]
            except (ValueError, TypeError):
                raise CustomValidationAPIError({
                    "categories": ["Las categorías deben ser IDs válidos."]
                })

            existing_categories = list(MovieCategory.objects.filter(
                id__in=category_ids).values_list('id', flat=True))
            if len(existing_categories) != len(category_ids):
                missing = set(category_ids) - set(existing_categories)
                raise CustomValidationAPIError({
                    "categories": [f"Las siguientes categorías no existen: {', '.join(map(str, missing))}."]
                })

            queryset = queryset.filter(
                categories__id__in=category_ids).distinct()

        # Validación del elenco (actores)
        actor_ids = data.getlist('cast')
        if actor_ids:
            try:
                actor_ids = [int(aid) for aid in actor_ids]
            except (ValueError, TypeError):
                raise CustomValidationAPIError({
                    "cast": ["Los actores deben ser IDs válidos."]
                })

            existing_actors = list(Actor.objects.filter(
                id__in=actor_ids).values_list('id', flat=True))
            if len(existing_actors) != len(actor_ids):
                missing = set(actor_ids) - set(existing_actors)
                raise CustomValidationAPIError({
                    "cast": [f"Los siguientes actores no existen: {', '.join(map(str, missing))}."]
                })

            queryset = queryset.filter(cast__id__in=actor_ids).distinct()

        return super().filter_queryset(queryset)
