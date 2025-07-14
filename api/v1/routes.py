from django.urls import path
from rest_framework import routers

from modules.manager.views.user import UserViewSet
from modules.movies.views.actors import ActorViewSet
from modules.movies.views.movie_category import MovieCategoryViewSet
from modules.movies.views.movie import MovieViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'actors', ActorViewSet, basename='actors')
router.register(r'movie-categories', MovieCategoryViewSet, basename='movie-categories')
router.register(r'movies', MovieViewSet, basename='movies')

urlpatterns = router.urls
