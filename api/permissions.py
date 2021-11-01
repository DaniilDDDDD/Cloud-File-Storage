from rest_framework import permissions


class RegistrationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


class FilePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        if request.method in ('PATCH', 'DELETE'):
            return (
                    request.user.is_authenticated and
                    request.user == obj.author
            )


class DownloadPermission(permissions.BasePermission):
    pass
