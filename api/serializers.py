import os
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.validators import MaxLengthValidator

from .models import File
from .validators import unique_username_validator, unique_email_validator

User = get_user_model()


class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class FileCreateSerializer(serializers.ModelSerializer):
    access = serializers.CharField(
        required=False
    )
    file = serializers.FileField(
        required=True,
        max_length=1000,
        allow_empty_file=False
    )

    def save(self, **kwargs):
        return super().save(
            author=self.context.get(
                'request'
            ).user,
            **kwargs
        )

    class Meta:
        model = File
        fields = ('id', 'access', 'file')


class FileUpdateSerializer(serializers.ModelSerializer):
    access = serializers.CharField(
        required=True
    )

    class Meta:
        model = File
        fields = ('access', 'id')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(
                254,
                message='Ensure email has at most 254 characters.'
            ),
            unique_email_validator
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure username value has at most 150 characters.'
            ),
            unique_username_validator
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure first_name has at most 150 characters.'
            )
        ]
    )
    last_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                150,
                message='Ensure last_name has at most 150 characters.'
            )
        ]
    )
    password = serializers.CharField(
        required=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password'
        )
