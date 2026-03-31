from django.urls import path

from .views import LoginView, MeView, PayoutRequestView, RegisterView


urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("users/me", MeView.as_view(), name="users-me"),
    path("seller/payout-requests", PayoutRequestView.as_view(), name="seller-payout-requests"),
]
