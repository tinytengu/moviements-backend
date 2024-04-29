from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Session

User = get_user_model()


# Models
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "info",
            "birthday",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "date_joined",
            "last_login",
        )


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = (
            "id",
            "user_agent",
            "ip_address",
            "user",
            "created_at",
            "updated_at",
        )


# Views
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignInResponseSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField()
