import uuid

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from tokens.authentication import AuthenticationData
from tokens.permissions import (
    IsRefreshToken,
    IsAccessToken,
)
from tokens.models import Blacklist

from .models import UserRequest, Session
from .serializers import (
    SignUpSerializer,
    SignInSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserSerializer,
    SessionSerializer,
)

User = get_user_model()


class SignUpView(APIView):
    def post(self, request: Request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer.instance.set_password(serializer.validated_data["password"])
        serializer.instance.save()

        verification_request = UserRequest.objects.create(
            user=serializer.instance,
            type=UserRequest.UserRequestType.SIGNUP_COMPLETE,
        )

        return Response(
            {"request_id": str(verification_request.id)},
            status=status.HTTP_201_CREATED,
        )


class SignUpCompleteView(APIView):
    def post(self, request: Request, request_id: str, *args, **kwargs):
        try:
            verification_request = UserRequest.objects.get(
                id=uuid.UUID(request_id),
                type=UserRequest.UserRequestType.SIGNUP_COMPLETE,
            )
        except (UserRequest.DoesNotExist, ValueError):
            return Response(
                {"error": "Invalid request id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        verification_request.user.is_active = True
        verification_request.user.save()
        verification_request.delete()

        return Response(
            {"response": "Registration completed"}, status=status.HTTP_200_OK
        )


class SignInView(APIView):
    def post(self, request: Request, *args, **kwargs):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(
                Q(username=serializer.validated_data["username"])
                | Q(email=serializer.validated_data["username"])
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_404_NOT_FOUND
            )

        if not user.check_password(serializer.validated_data["password"]):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "User is not active"}, status=status.HTTP_403_FORBIDDEN
            )

        session = Session.create_for_user(
            user, request.META["HTTP_USER_AGENT"], request.META["REMOTE_ADDR"]
        )
        session.updated_at = timezone.now()
        session.save()
        access_token, refresh_token = session.create_token_pair()

        return Response(
            {"access_token": access_token, "refresh_token": refresh_token},
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    permission_classes = [IsRefreshToken]

    def post(self, request: Request, *args, **kwargs):
        auth: AuthenticationData = request.auth

        Blacklist.blacklist_refresh_token(str(auth.token))

        access_token, refresh_token = auth.session.create_token_pair()

        return Response(
            {"access_token": access_token, "refresh_token": refresh_token},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    def post(self, request: Request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(
                Q(username=serializer.validated_data["username"])
                | Q(email=serializer.validated_data["username"])
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_403_FORBIDDEN
            )

        # Delete all previous password reset requests
        UserRequest.objects.filter(
            user=user,
            type=UserRequest.UserRequestType.PASSWORD_RESET,
        ).delete()

        reset_request = UserRequest.objects.create(
            user=user,
            type=UserRequest.UserRequestType.PASSWORD_RESET,
        )

        return Response(
            {"request_id": str(reset_request.id)}, status=status.HTTP_201_CREATED
        )


class PasswordResetView(APIView):
    def post(self, request: Request, request_id: str, *args, **kwargs):
        try:
            reset_request = UserRequest.objects.get(
                id=uuid.UUID(request_id),
                type=UserRequest.UserRequestType.PASSWORD_RESET,
            )
        except (UserRequest.DoesNotExist, ValueError):
            return Response(
                {"error": "Invalid request id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_request.user.set_password(serializer.validated_data["new_password"])
        reset_request.user.save()

        reset_request.user.sessions.all().delete()

        reset_request.delete()

        return Response({"response": "Password changed"}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAccessToken]

    def get(self, request: Request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        session = request.auth.session

        return Response(
            {
                "user": serializer.data,
                "session": {
                    "id": str(session.id),
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                },
            },
            status=status.HTTP_200_OK,
        )


class SessionView(APIView):
    permission_classes = [IsAccessToken]

    def get(self, request: Request, session_id: str, *args, **kwargs):
        try:
            session = Session.objects.get(id=uuid.UUID(session_id))
        except Session.DoesNotExist:
            return Response(
                {"error": "Invalid session id"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, session)

        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, session_id: str, *args, **kwargs):
        try:
            session = Session.objects.get(id=uuid.UUID(session_id))
        except Session.DoesNotExist:
            return Response(
                {"error": "Invalid session id"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, session)

        session.delete()
        return Response({"response": "Session deleted"}, status=status.HTTP_200_OK)


class SessionsView(APIView):
    permission_classes = [IsAccessToken]

    def get(self, request: Request, *args, **kwargs):
        http_request = request._request
        if not http_request.token_session or not http_request.token_user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = SessionSerializer(
            http_request.token_user.sessions.all(), many=True
        )
        return Response({"sessions": serializer.data}, status=status.HTTP_200_OK)
