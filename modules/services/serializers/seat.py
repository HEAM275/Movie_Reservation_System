from rest_framework import serializers
from collections import defaultdict
from modules.services.models.reservation import Seat


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'is_reserved']



class SeatMapSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # Agrupa los asientos por fila y ordena por número
        seats = instance.seats.all().order_by('row', 'number')
        grouped = defaultdict(list)

        for seat in seats:
            grouped[seat.row].append({
                'number': seat.number,
                'is_reserved': seat.is_reserved,
                'id': seat.id
            })

        # Devuelve un listado de filas con sus asientos
        return {
            row: sorted(row_seats, key=lambda x: x['number'])
            for row, row_seats in grouped.items()
        }