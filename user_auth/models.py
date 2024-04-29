import uuid
from typing import ClassVar

from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

from tokens.jwt import generate_token_pair

from .mixins import OwnedModelMixin


class CustomUserManager(UserManager):
    def create_superuser(self, *args, **kwargs):
        user = super().create_user(*args, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        max_length=255,
        blank=False,
        unique=True,
        error_messages={"unique": _("A user with that email already exists.")},
    )
    info = models.TextField(
        _("basic info"),
        null=True,
        blank=True,
        help_text=_("Basic user info displayed in profile"),
    )
    birthday = models.DateField(_("birthday"), null=True, blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects: ClassVar[CustomUserManager] = CustomUserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Session(OwnedModelMixin):
    objects: models.Manager["Session"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sessions"
    )
    user_agent = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    OWNER_FIELD = "user"

    def create_token_pair(self):
        """
        Generates and returns a pair of access and refresh tokens associated with the current session.

        Returns:
            A tuple containing the access token and the refresh token.
        """
        access_token, refresh_token = generate_token_pair({"session_id": str(self.id)})
        return access_token, refresh_token

    @classmethod
    def create_for_user(cls, user, user_agent: str, ip_address: str) -> "Session":
        """
        Creates a new session for the given user with the specified user agent and IP address.

        Args:
            user (AbstractBaseUser): The user for whom the session is being created.
            user_agent (str): The user agent string associated with the session.
            ip_address (str): The IP address from which the session is being created.

        Returns:
            Session: The newly created session object.
        """
        session = cls.objects.create(
            user=user, user_agent=user_agent, ip_address=ip_address
        )
        return session

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")


class UserRequest(models.Model):
    objects: models.Manager["UserRequest"]

    class UserRequestType(models.TextChoices):
        SIGNUP_COMPLETE = "signup_complete", _("signup complete")
        PASSWORD_RESET = "password_reset", _("password reset")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(
        max_length=255,
        choices=UserRequestType.choices,
        default=UserRequestType.SIGNUP_COMPLETE.value,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="verification_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
