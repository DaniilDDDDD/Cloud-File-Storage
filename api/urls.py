from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, FileViewSet

router = DefaultRouter()
router.register(
    'users',
    UserViewSet,
    basename='users'
)
router.register(
    'files',
    FileViewSet,
    basename='files'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
