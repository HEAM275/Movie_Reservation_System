from django.contrib import admin
from modules.movies.models.movies import Movie, MovieCategory, Actor

# Register your models here.

admin.site.register(Movie)
admin.site.register(MovieCategory)
admin.site.register(Actor)
