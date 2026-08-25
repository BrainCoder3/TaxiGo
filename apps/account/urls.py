from django.urls import path

from .views import (
    CSRFTokenView,
    RegisterView,
    LoginView,
    RefreshView,
    LogoutView,
    MeView,
    VerifyEmailView,
)


urlpatterns = [
    path(
        "csrf/",
        CSRFTokenView.as_view(),
        name='csrf'
    ),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        RefreshView.as_view(),
        name="refresh",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
]