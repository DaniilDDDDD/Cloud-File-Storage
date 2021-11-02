from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import File

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    empty_value_display = '-пусто-'
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'access', 'file', 'download_count')
    empty_value_display = '-пусто-'
    search_fields = ('access', 'author', 'file')
    list_filter = ('access', 'download_count', 'author')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(File, FileAdmin)
