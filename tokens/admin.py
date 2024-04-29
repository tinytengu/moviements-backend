from django.contrib import admin

from .models import Blacklist


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token_type",
        "token",
        "expires_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    list_filter = ("token_type",)
    search_fields = ("token", "token_type")
