from django.urls import path
from rest_framework.routers import DefaultRouter


from .views import (
    DriverMeView,
    DriverPositionView,
    DriverStatusView,
    VehicleViewSet,
)

router = DefaultRouter()

router.register(
    "vehicles",
    VehicleViewSet,
    basename="vehicle"
)

urlpatterns = [
    path("drivers/me/",DriverMeView.as_view(),name="driver-me"),
    path("drivers/me/position/",DriverPositionView.as_view(),name="driver-position",),
    path("drivers/me/status/",DriverStatusView.as_view(),name="driver-status")
]

urlpatterns += router.urls