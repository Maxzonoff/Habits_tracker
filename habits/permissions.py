from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение:
    - Чтение (GET) — любой авторизованный пользователь
    - Изменение/удаление (PUT, PATCH, DELETE) — только владелец
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user
