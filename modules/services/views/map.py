from collections import defaultdict
from django.utils.translation import gettext_lazy as _

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from modules.services.models.showtime import Showtime

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa

@swagger_auto_schema(tags=["Reservations"])
class SeatMapView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary=_("Mostrar mapa de asientos"),
        manual_parameters=[
            oa.Parameter('showtime_id', oa.IN_QUERY, description="ID de la función", type=oa.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        showtime_id = request.query_params.get('showtime_id')
        if not showtime_id:
            return Response({'error': _('showtime_id es requerido')}, status=400)

        try:
            showtime = Showtime.objects.get(id=showtime_id)
            seats = showtime.seats.all().order_by('row', 'number')

            grouped = defaultdict(list)
            for seat in seats:
                grouped[seat.row].append({
                    'number': seat.number,
                    'is_reserved': seat.is_reserved,
                    'id': seat.id
                })

            return Response(dict(grouped), status=200)
        except Showtime.DoesNotExist:
            return Response({'error': _('Función no encontrada')}, status=404)