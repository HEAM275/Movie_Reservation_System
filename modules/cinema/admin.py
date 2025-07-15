from django.contrib import admin
from modules.cinema.models.cinema import Cinema
from modules.cinema.models.screening_room import ScreeningRoom

# Register your models here.

admin.site.register(Cinema)
admin.site.register(ScreeningRoom)  