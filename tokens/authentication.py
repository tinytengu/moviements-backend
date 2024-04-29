from dataclasses import dataclass

from django.utils import timezone

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from rest_framework.request import Request

from user_auth.models import Session

from .jwt import decode_token, get_token_type
from .jwt.types import TokenType
from .models import Blacklist


@dataclass(frozen=True)
class AuthenticationData:
    token: str
    token_type: TokenType
    session: Session

    @property
    def payload(self):
        return decode_token(self.token)


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        header = get_authorization_header(request)
        if header:
            token = header.decode("utf-8").replace("Bearer ", "")
        else:
            token = request.COOKIES.get("access_token", None)

        if not token:
            return None

        try:
            token_payload = decode_token(token)
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        if Blacklist.objects.filter(token=token):
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        try:
            token_session = Session.objects.get(id=str(token_payload.get("session_id")))
        except Session.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid session")

        if token_session.user.is_active is False:
            raise exceptions.AuthenticationFailed("User is inactive")

        token_session.save()
        token_session.user.last_login = timezone.now()
        token_session.user.save()

        if (
            token_session.user_agent != request.META["HTTP_USER_AGENT"]
            or token_session.ip_address != request.META["REMOTE_ADDR"]
        ):
            token_session.delete()
            raise exceptions.AuthenticationFailed(
                "Invalid session fingerprint. Logged out."
            )

        payload = AuthenticationData(
            token=token, session=token_session, token_type=get_token_type(token)
        )

        return (token_session.user, payload)
