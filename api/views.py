import os
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status

from bebranie.settings import MEDIA_ROOT
from .permissions import RegistrationPermission, FilePermissions
from .paginators import VariablePageSizePaginator
from .serializers import (
    UserCreateSerializer, FileCreateSerializer, FileUpdateSerializer,
    FileListSerializer
)
from .models import File

User = get_user_model()


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [FilePermissions]
    pagination_class = VariablePageSizePaginator
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

        if request.user.is_authenticated:
            queryset = queryset.filter(
                Q(access='public') | Q(author=request.user)
            )
        else:
            queryset = queryset.filter(access='public')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=True,
        url_path='link',
        permission_classes=[FilePermissions],
        url_name='link'
    )
    def file_link(self, request, id):
        file = self.get_object()
        name = file.file.name.split('/')[-1]
        view_link = request.build_absolute_uri(reverse('view_file', args={name}))
        download_link = request.build_absolute_uri(reverse('download_file', args={name}))
        return Response(
            data={
                'id': file.id,
                'view_link': view_link,
                'download_link': download_link
            }
        )


@api_view(['GET'])
def view_file(request, filename):
    file = get_object_or_404(File, file__endswith=filename)
    if file.access == 'public' or (
            file.access == 'by_link' and
            request.user and
            request.user.is_authenticated
    ) or (
            request.user and
            file.author == request.user
    ):
        return FileResponse(open(f'media/{file.file.name}', 'rb'))
    return Response(
        data={"detail": "You do not have permission to perform this action."},
        status=status.HTTP_403_FORBIDDEN
    )


@api_view(['GET'])
def download_file(request, filename):
    file = get_object_or_404(File, file__endswith=filename)
    if file.access == 'public' or (
            file.access == 'by_link' and
            request.user and
            request.user.is_authenticated
    ) or (
            request.user and
            file.author == request.user
    ):
        with open(f'media/{file.file.name}', 'rb') as f:
            data = f.read()
        file.download_count += 1
        file.save()
        ext = file.file.name.split('.')[-1]
        response = HttpResponse(data, content_type=f'application/{ext}')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response

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
