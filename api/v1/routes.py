from django.urls import path
from rest_framework import routers

from modules.manager.views.user import UserViewSet
from modules.movies.views.actors import ActorViewSet
from modules.movies.views.movie_category import MovieCategoryViewSet
from modules.movies.views.movie import MovieViewSet
from modules.cinema.views.cinema import CinemaViewSet
from modules.cinema.views.screening_room import ScreeningRoomViewSet
from modules.services.views.showtime import ShowtimeViewSet
from modules.services.views.reservation import ReservationViewSet
from modules.services.views.map import SeatMapView

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'actors', ActorViewSet, basename='actors')
router.register(r'movie-categories', MovieCategoryViewSet, basename='movie-categories')
router.register(r'movies', MovieViewSet, basename='movies')
router.register(r'cinemas', CinemaViewSet, basename='cinemas')
router.register(r'screening-rooms', ScreeningRoomViewSet, basename='screening-rooms')
router.register(r'showtimes', ShowtimeViewSet, basename='showtimes')
router.register( r'reservations', ReservationViewSet, basename='reservations')


urlpatterns = router.urls + [ path('map/', SeatMapView.as_view(), name='map')]
