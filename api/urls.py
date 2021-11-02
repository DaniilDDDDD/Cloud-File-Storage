from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, FileViewSet, download_file, view_file

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
    path('files/view/<str:filename>/', view_file, name='view_file'),
    path('files/download/<str:filename>/', download_file, name='download_file'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
