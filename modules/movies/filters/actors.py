import django_filters
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from movies.models import Actor


class CustomValidationAPIError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error de validación.'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class ActorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    birth_date = django_filters.DateFilter(
        field_name='birth_date', lookup_expr='exact'
    )

    class Meta:
        model = Actor
        fields = ['name', 'birth_date']

    def filter_queryset(self, queryset):
        # Obtener los valores de los filtros desde `data`
        name = self.data.get('name')
        birth_date = self.data.get('birth_date')

        # Validación para 'name'
        if name is not None:
            name = name.strip()
            if not name:
                raise CustomValidationAPIError({
                    "name": ["El nombre no puede estar vacío si se proporciona."]
                })

            # Filtrar manualmente y validar resultados
            queryset = queryset.filter(name__icontains=name)
            if not queryset.exists():
                raise CustomValidationAPIError({
                    "name": [f"No se encontró ningún actor con el nombre '{name}'."]
                })

        # Validación para 'birth_date'
        if birth_date:
            try:
                # Intentar parsear la fecha usando el formato correcto
                from datetime import datetime
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                raise CustomValidationAPIError({
                    "birth_date": ["Fecha inválida. Use el formato YYYY-MM-DD."]
                })

            # Aplicar filtro por fecha
            queryset = queryset.filter(birth_date=birth_date)

            if not queryset.exists():
                raise CustomValidationAPIError({
                    "birth_date": [f"No se encontró ningún actor nacido el {birth_date}."]
                })

        return super().filter_queryset(queryset)
