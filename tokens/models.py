import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone

from tokens.jwt.types import TokenType
from tokens.jwt import decode_token, decode_token_no_exp, get_token_type


class Blacklist(models.Model):
    objects: models.Manager["Blacklist"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_type = models.CharField(max_length=255, blank=False, null=False)
    token = models.TextField(max_length=1024, blank=False, null=False)
    expires_at = models.DateTimeField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def from_token(cls, token: str, verify_exp: bool = False):
        payload = decode_token_no_exp(token)
        cls.objects.create(
            token=token,
            token_type=get_token_type(token).value,
            expires_at=datetime.fromtimestamp(payload.get("exp", 0)),
        )

    @classmethod
    def blacklist_refresh_token(cls, refresh_token: str):
        refresh_token_payload = decode_token_no_exp(refresh_token)

        cls.objects.create(
            token=refresh_token,
            token_type=TokenType.REFRESH.value,
            expires_at=datetime.fromtimestamp(
                refresh_token_payload.get("exp", timezone.now().timestamp())
            ),
        )

        try:
            access_token = str(refresh_token_payload.get("access_token"))
            access_token_payload = decode_token(access_token)

            cls.objects.create(
                token=access_token,
                token_type=TokenType.ACCESS.value,
                expires_at=datetime.fromtimestamp(
                    access_token_payload.get("exp", timezone.now().timestamp())
                ),
            )
        except Exception:
            pass
