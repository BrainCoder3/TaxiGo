from rest_framework.permissions import BasePermission

class IsDriver(BasePermission):
    message = "Only drivers can access this endpoint"
    def has_permission(self, request, view):
        
        return (
            request.user.is_authenticated
            and request.user.role == 'DRIVER'
        )
    
class IsVehicleOwnerOrAdmin(BasePermission):
    message = "You do not have permission to manage this vehicle"
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "ADMIN":
            return True
        return obj.driver.user == request.user


class IsDriverOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and (request.user.role == "DRIVER" or request.user.role == "ADMIN"))