from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.http import HttpRequest
from django.db.models import Q

from .models import Session

User = get_user_model()


class AuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest | None, **kwargs):
        username, password = kwargs.get("username"), kwargs.get("password")

        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        user_agent = request.META["HTTP_USER_AGENT"] if request else "Internal"
        remote_addr = request.META["REMOTE_ADDR"] if request else "127.0.0.1"

        session, created = Session.objects.get_or_create(
            user=user, user_agent=user_agent, ip_address=remote_addr
        )

        if not created:
            session.updated_at = timezone.now()
            session.save()

        return user

    def get_user(self, user_id) -> AbstractBaseUser | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_permissions(self, user_obj, obj=None):
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None):
        return perm in self.get_all_permissions(user_obj, obj=obj)
