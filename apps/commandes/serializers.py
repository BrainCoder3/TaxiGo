from rest_framework import serializers
from .models import Ride,FareGrid
from apps.taxis.utils import (
    haversine_distance,
    calculate_price,
)
from decimal import Decimal


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ['id','passenger','driver','departure_latitude','departure_longitude','arrival_latitude','arrival_longitude',
                  'distance_km','estimated_price','status','created_at'
                  ]
        read_only_fields = ['id','passenger','driver','distance_km','estimated_price','status','created_at']


class RideCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = [
                "departure_latitude",
                "departure_longitude",
                "arrival_latitude",
                "arrival_longitude",
            ]

    def validate_departure_latitude(self,value):
        if value < -90 or value > 90 :
            raise serializers.ValidationError("The departure Latitude must be between -90 and 90 ")
        return value

    def validate_departure_longitude(self,value):
        if value < -180 or value > 180 :
            raise serializers.ValidationError("The departure longitude must be between -180 and 180")
        return value


    def validate_arrival_latitude(self,value):
        if value < -90 or value > 90 :
            raise serializers.ValidationError("The arrival Latitude must be between -90 and 90 ")
        return value

    def validate_arrival_longitude(self,value):
        if value < -180 or value > 180 :
            raise serializers.ValidationError("The arrival longitude must be between -180 and 180")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        passenger = request.user

        if Ride.objects.filter(
            passenger=passenger,
            status__in=[
                Ride.StatusType.WAITING,
                Ride.StatusType.ACCEPTED,
                Ride.StatusType.IN_PROGRESS
            ]
        ).exists():
            raise serializers.ValidationError("You already have an active ride")
        return attrs

    def create(self, validated_data):
        departure_lat = validated_data["departure_latitude"]
        departure_lon = validated_data["departure_longitude"]
        arrival_lat = validated_data["arrival_latitude"]
        arrival_lon = validated_data["arrival_longitude"]

        distance = haversine_distance(departure_lat,departure_lon,arrival_lat,arrival_lon)

        distance_converted = Decimal(str(distance))
        distance_converted = distance_converted.quantize(Decimal("0.001"))

        fare_grid = FareGrid.objects.filter(
            active=True
        ).first()

        if fare_grid is None:
            raise serializers.ValidationError("No active fare grid is configured")

        price = calculate_price(
            distance_converted,
            fare_grid.pickup_price,
            fare_grid.price_per_km
        )
        price = price.quantize(Decimal("0.01"))

        return Ride.objects.create(
                passenger=self.context["request"].user,
                departure_latitude=departure_lat,
                departure_longitude=departure_lon,
                arrival_latitude=arrival_lat,
                arrival_longitude=arrival_lon,
                distance_km=distance_converted,
                estimated_price=price,
            )


class RideStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Ride.StatusType.choices
    )
    







