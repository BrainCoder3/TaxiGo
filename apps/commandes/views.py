from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated

from apps.commandes.models import Ride
from .permissions import IsPassenger
from rest_framework.decorators import action
from .serializers import (RideCreateSerializer,RideSerializer,RideStatusSerializer,)
from rest_framework.response import Response
from rest_framework import status
from apps.taxis.permissions import IsDriver
from apps.taxis.models import Driver

from django.db import transaction
# Create your views here.


class RideViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    
    def get_serializer_class(self):
        if self.action == "create":
            return RideCreateSerializer
        if self.action =="update_status":
            return RideStatusSerializer
        return RideSerializer

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsPassenger(),
            ]
        if self.action == "accept":
            return [IsAuthenticated(),IsDriver()]
        if self.action == "update_status":
            return [
                IsAuthenticated(),
                IsDriver(),
            ]
        if self.action == "cancel":
            return [
                IsAuthenticated(),
                IsPassenger(),
            ]
        if self.action == "available":
            return [
                IsAuthenticated(),
                IsDriver(),
            ]
        return [
            IsAuthenticated(),
        ]


    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Ride.objects.all()

        if user.role == "DRIVER":
            if self.action == 'accept':
                return Ride.objects.filter(status=Ride.StatusType.WAITING,driver__isnull=True)
            return Ride.objects.filter(driver__user=user)
        
        return Ride.objects.filter(passenger=user)

    @action(
        detail=True,
        methods=["patch"],
        url_path="accept",
    )
    def accept(self, request, pk=None):
        
        with transaction.atomic():
            ride = Ride.objects.select_for_update().filter(
                pk=pk,
                status=Ride.StatusType.WAITING,
                driver__isnull=True
            ).first()
            driver = Driver.objects.select_for_update().filter(
                        user=request.user
                    ).first()

            if ride is None:
                return Response(
                    {"detail": "Ride is no longer available."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if driver is None:
                return Response(
                    {"detail": "Driver profile does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if driver.availability_status != Driver.StatusType.AVAILABLE:
                return Response(
                    {"detail": "Driver must be available to accept a ride."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Ride.objects.filter(
                driver=driver,
                status__in=[
                    Ride.StatusType.ACCEPTED,
                    Ride.StatusType.IN_PROGRESS,
                ]
            ).exists():
                return Response(
                    {"detail": "You already have an active ride."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ride.driver = driver
            ride.status = Ride.StatusType.ACCEPTED

            driver.availability_status = Driver.StatusType.ON_A_RIDE

            ride.save(update_fields=["driver", "status"])
            driver.save(update_fields=["availability_status"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    def update_status(self, request, pk=None):
        with transaction.atomic():
            ride = Ride.objects.select_for_update().filter(
                pk=pk,
                driver__user=request.user
            ).first()
            if ride is None:
                return Response(
                        {"detail": "Ride not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

            serializer = RideStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            requested_status = serializer.validated_data['status']

            allowed_transitions = {
                Ride.StatusType.ACCEPTED: Ride.StatusType.IN_PROGRESS,
                Ride.StatusType.IN_PROGRESS: Ride.StatusType.COMPLETED,
            }
            expected_status = allowed_transitions.get(ride.status)

            if requested_status != expected_status :
                return Response(
                    {"detail": "Invalid ride status transition"},
                    status=status.HTTP_400_BAD_REQUEST)

            ride.status = requested_status
            ride.save(update_fields=["status"])
            if requested_status == Ride.StatusType.COMPLETED:
                driver = Driver.objects.select_for_update().get(
                            pk=ride.driver_id
                        )
                driver.availability_status = Driver.StatusType.AVAILABLE
                driver.save(update_fields=["availability_status"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )


    @action(
        detail=True,
        methods=["patch"],
        url_path="cancel",
    )
    def cancel(self, request, pk=None):

        with transaction.atomic():

            ride = Ride.objects.select_for_update().filter(
                pk=pk,
                passenger=request.user
            ).first()

            if ride is None:
                return Response(
                    {"detail": "Ride not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            cancellable_statuses = [
                Ride.StatusType.WAITING,
                Ride.StatusType.ACCEPTED,
            ]

            if ride.status not in cancellable_statuses:
                return Response(
                    {"detail": "Ride cannot be cancelled at this stage."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            driver = None

            if ride.driver_id is not None:
                driver = Driver.objects.select_for_update().get(
                    pk=ride.driver_id
                )

            ride.status = Ride.StatusType.CANCELLED
            ride.save(
                update_fields=["status"]
            )

           
            if driver is not None:
                driver.availability_status = Driver.StatusType.AVAILABLE
                driver.save(
                    update_fields=["availability_status"]
                )

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )
    @action(
        detail=False,
        methods=["get"],
        url_path="available",
    )
    def available(self, request):
        rides = Ride.objects.filter(
            status=Ride.StatusType.WAITING,
            driver__isnull=True
        )
        serializer = RideSerializer(
            rides,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    