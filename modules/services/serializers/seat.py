from rest_framework import serializers
from collections import defaultdict
from modules.services.models.reservation import Seat


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'is_reserved']




class SeatMapSerializer(serializers.Serializer):
    def to_representation(self, instance):
        seats = instance.seats.all().order_by('row', 'number')
        grouped = defaultdict(list)

        for seat in seats:
            grouped[seat.row].append({
                'number': seat.number,
                'is_reserved': seat.is_reserved,
                'id': seat.id
            })

        return dict(grouped)