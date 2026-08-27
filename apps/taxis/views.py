from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.commandes.permissions import IsPassenger
from .permissions import IsDriver,IsDriverOrAdmin, IsVehicleOwnerOrAdmin
from .serializers import DriverCreateSerializer, DriverSerializer,DriverPositionSerializer,DriverStatusSerializer, VehicleSerializer,NearbyDriversQuerySerializer, NearbyDriverSerializer
from .models import Driver, Vehicle
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from apps.taxis.utils import haversine_distance
from decimal import Decimal
# Create your views here.

class DriverMeView(APIView):
    permission_classes =[
        IsAuthenticated,
        IsDriver,
    ]
    def post(self,request):
        if Driver.objects.filter(user=request.user).exists():
            return Response(
                {'detail':'DRIVER profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DriverCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save(user=request.user)
        return Response(
            DriverSerializer(driver).data,
            status=status.HTTP_201_CREATED
        )

    def get(self,request):
        driver = Driver.objects.filter(user=request.user).first()
        if driver is None:
            return Response(
                {'detail':'DRIVER profile does not exist'},
                status=status.HTTP_404_NOT_FOUND

            )
        serializer = DriverSerializer(driver)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class DriverPositionView(APIView):
    permission_classes =[IsAuthenticated,IsDriver]

    def patch(self,request):
        driver = Driver.objects.filter(user=request.user).first()

        if driver is None:
            return Response(
                {'detail':'DRIVER profile does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = DriverPositionSerializer(driver,data=request.data)
        serializer.is_valid(raise_exception=True)
        driver_updated = serializer.save()

        return Response(
            DriverSerializer(driver_updated).data,
            status=status.HTTP_200_OK
        )
        

class DriverStatusView(APIView):
    permission_classes =[
        IsAuthenticated,
        IsDriver
    ]
    def patch(self,request):
        driver = Driver.objects.filter(user=request.user).first()
        if driver is None:
            return Response(
                    {'detail':'DRIVER profile does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        serializer = DriverStatusSerializer(driver,data=request.data)
        serializer.is_valid(raise_exception=True)
        driver_updated = serializer.save()

        return Response(
            DriverSerializer(driver_updated).data,
            status=status.HTTP_200_OK
        )
        



class VehicleViewSet(ModelViewSet):
    serializer_class = VehicleSerializer
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(),IsDriver()]
        return [IsAuthenticated(),IsDriverOrAdmin(),IsVehicleOwnerOrAdmin()]

        
    def get_queryset(self):
        if self.request.user.role == "ADMIN":
            return Vehicle.objects.all()
        return Vehicle.objects.filter(
            driver__user=self.request.user
        )
    def perform_create(self,serializer):
        driver = Driver.objects.filter(
                    user=self.request.user
                ).first()
        if driver is None :
            raise ValidationError(
                    "You must create a driver profile before adding a vehicle."
                )
        serializer.save(driver=driver)
        

class NearbyDriversView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsPassenger,
    ]

    def get(self, request):

        query_serializer = NearbyDriversQuerySerializer(
            data=request.query_params
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        passenger_lat = query_serializer.validated_data["lat"]
        passenger_lon = query_serializer.validated_data["lon"]
        limit = query_serializer.validated_data["limit"]

        radius = query_serializer.validated_data.get(
            "radius"
        )

        drivers = Driver.objects.filter(
            availability_status=Driver.StatusType.AVAILABLE,
            latitude__isnull=False,
            longitude__isnull=False,
        )

        results = []

        for driver in drivers:

            distance = haversine_distance(
                passenger_lat,
                passenger_lon,
                driver.latitude,
                driver.longitude,
            )

            distance = Decimal(str(distance)).quantize(
                Decimal("0.001")
            )

            if radius is not None and distance > radius:
                continue

            results.append({
                "id": driver.id,
                "latitude": driver.latitude,
                "longitude": driver.longitude,
                "distance_km": distance,
            })

        # Ici on est SORTI de la boucle

        results.sort(
            key=lambda item: item["distance_km"]
        )

        results = results[:limit]

        serializer = NearbyDriverSerializer(
            results,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )