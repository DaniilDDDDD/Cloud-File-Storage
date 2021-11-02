import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

User = get_user_model()


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = uuid.uuid4().hex + '.' + ext
    return os.path.join(os.path.join('files', str(instance.author.pk)), filename)


class File(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        related_name='files',
        verbose_name='Author',
        on_delete=models.CASCADE
    )
    access = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        default='only_author',
        verbose_name='Access'
    )
    file = models.FileField(
        blank=False,
        null=False,
        upload_to=upload_to,
        verbose_name='File',
        unique=True
    )

    download_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        blank=False,
        null=False,
        default=0,
        verbose_name='Download counter'
    )

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

        ordering = ['-download_count']
