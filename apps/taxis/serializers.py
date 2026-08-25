from rest_framework import serializers
from .models import Driver, Vehicle
from django.utils import timezone

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id','user','license_number','availability_status','latitude','longitude','location_updated_at','created_at','updated_at']
        read_only_fields = ['id','user','created_at','updated_at','location_updated_at','availability_status','latitude','longitude']


class DriverCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields =['license_number']
        

class DriverPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = ["latitude", "longitude"]

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        return value

    def validate(self, attrs):
        if (
            "latitude" not in attrs
            or attrs.get("latitude") is None
            or "longitude" not in attrs
            or attrs.get("longitude") is None
        ):
            raise serializers.ValidationError(
                "Latitude and longitude are required."
            )

        return attrs

    def update(self, instance, validated_data):
        instance.latitude = validated_data["latitude"]
        instance.longitude = validated_data["longitude"]
        instance.location_updated_at = timezone.now()

        instance.save()

        return instance


class DriverStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields =['availability_status']

    def validate_availability_status(self,value):
        if value == Driver.StatusType.ON_A_RIDE:
            raise serializers.ValidationError(
                "ON_A_RIDE cannot be set manually."
            )
        return value


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','driver','brand','model','registration_number','seats','vehicle_type','created_at','updated_at']
        read_only_fields = ['id','driver','created_at','updated_at']

    def validate_seats(self,value):
        if value < 1 :
            raise serializers.ValidationError("Vehicle must have at least one seat")
        return value

    def validate_registration_number(self,value):
        return value.strip().upper()
    