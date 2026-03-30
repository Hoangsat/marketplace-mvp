from django.urls import path

from .views import LoginView, MeView, RegisterView


urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("users/me", MeView.as_view(), name="users-me"),
]
