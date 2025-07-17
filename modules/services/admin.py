from django.contrib import admin
from modules.services.models.reservation import Reservation,Seat,ReservationGroup 
from modules.services.models.showtime import Showtime

# Register your models here.

admin.site.register(Reservation)
admin.site.register(Showtime)  
admin.site.register(Seat)
admin.site.register(ReservationGroup)
