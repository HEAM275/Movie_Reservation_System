from django.urls import path
from rest_framework import routers

from modules.manager.views.user import UserViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')

urlpatterns = router.urls
