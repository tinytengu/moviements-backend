from django.urls import path

from .views import (
    SignUpView,
    SignUpCompleteView,
    SignInView,
    RefreshView,
    MeView,
    PasswordResetRequestView,
    PasswordResetView,
    SessionView,
    SessionsView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="sign_up"),
    path(
        "signup/complete/<request_id>",
        SignUpCompleteView.as_view(),
        name="sign_up_complete",
    ),
    path("signin/", SignInView.as_view(), name="sign_in"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path(
        "reset-password/",
        PasswordResetRequestView.as_view(),
        name="reset_password_request",
    ),
    path(
        "reset-password/<request_id>/",
        PasswordResetView.as_view(),
        name="reset_password_complete",
    ),
    path("me/", MeView.as_view(), name="me"),
    path("sessions/<session_id>/", SessionView.as_view(), name="session"),
    path("sessions/", SessionsView.as_view(), name="sessions"),
]
