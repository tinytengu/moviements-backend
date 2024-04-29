from rest_framework.permissions import BasePermission

from .jwt.types import TokenType


class IsRefreshToken(BasePermission):
    """A custom permission class that checks if the token is an refresh token."""

    def has_permission(self, request, view):
        return request.auth.token_type == TokenType.REFRESH


class IsAccessToken(BasePermission):
    """A custom permission class that checks if the token is an access token."""

    def has_permission(self, request, view):
        return request.auth.token_type == TokenType.ACCESS

    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False

        if request.user.is_superuser:
            return True

        if not hasattr(obj, "get_owner"):
            return True

        return obj.get_owner() == request.user
