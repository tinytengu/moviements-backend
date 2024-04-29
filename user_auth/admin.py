from datetime import datetime

from django.contrib import admin
from django.utils import timezone

from .models import CustomUser, Session, UserRequest


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0
    show_change_link = True
    classes = ("collapse",)
    fields = ("id", "user_agent", "ip_address", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Basic info",
            {
                "fields": (
                    "id",
                    "username",
                    "email",
                    "password",
                    "info",
                    "birthday",
                    "date_joined",
                    "get_last_login",
                )
            },
        ),
        (
            "Statuses",
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        (
            "Permissions",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("id", "date_joined", "get_last_login")
    search_fields = ("id", "username", "email")

    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "get_last_login",
        "get_user_sessions_count",
    )
    list_display_links = ("id", "username", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")

    inlines = (SessionInline,)

    @admin.display(description="Last login")
    def get_last_login(self, obj: CustomUser) -> datetime:
        """
        This method returns the last login timestamp for the given user.

        Args:
            obj (CustomUser): The user object for which the last login timestamp is to be retrieved.

        Returns:
            datetime: The timestamp of the last login for the given user. If the user has never logged in, it returns the current time.
        """
        session = obj.sessions.order_by("-updated_at").first()
        if not session:
            return timezone.now()
        return session.updated_at

    @admin.display(description="Active sessions")
    def get_user_sessions_count(self, obj: CustomUser) -> int:
        """
        This method returns the count of active sessions for the given user.

        Args:
            obj (CustomUser): The user object for which the active sessions count is to be retrieved.

        Returns:
            int: The count of active sessions for the given user.
        """
        return obj.sessions.order_by("-updated_at").all().count()


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ip_address", "created_at", "updated_at")
    list_filter = ("user", "ip_address")
    search_fields = ("user", "user_agent", "ip_address")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "user",
        "created_at",
    )
    readonly_fields = ("id", "created_at")
