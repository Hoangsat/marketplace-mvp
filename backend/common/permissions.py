from rest_framework.permissions import BasePermission


class IsAuthenticatedSeller(BasePermission):
    message = "Seller account required"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_seller", False))
