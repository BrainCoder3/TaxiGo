from rest_framework.permissions import BasePermission

class IsPassenger(BasePermission):
    message = "Only passengers can perform this action."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "CLIENT"
        )