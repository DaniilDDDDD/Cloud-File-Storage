import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.views import serve
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status

from bebranie.settings import MEDIA_ROOT
from .permissions import RegistrationPermission, FilePermissions, DownloadPermission
from .serializers import (
    UserCreateSerializer, FileCreateSerializer, FileUpdateSerializer,
    FileListSerializer
)
from .models import File

User = get_user_model()


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [FilePermissions]
    queryset = File.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return FileUpdateSerializer
        elif self.request.method == 'POST':
            return FileCreateSerializer
        else:
            return FileListSerializer

    def perform_destroy(self, instance):
        try:
            os.remove(MEDIA_ROOT + '/' + str(instance.file))
        except PermissionError:
            pass
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.filter(
            Q(access='public') | Q(author=request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # TODO: переделать возвращение файла
    @action(
        detail=False,
        methods=['GET'],
        url_path='download/(?P<link>[^/.]+)/'
    )
    def download_file(self, request, link):
        link = link.split('media/')[-1]
        file = get_object_or_404(File, file=link)
        if file.access in ('public', 'by_link'):
            return serve(request, file.file)
        return Response(
            data={"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [RegistrationPermission, ]
    http_method_names = ['post', ]
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        if 'password' in serializer.data:
            instance.set_password(serializer.data['password'])
            instance.save()
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['id'] = instance.id
        del data['password']
        return Response(
            data=data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
