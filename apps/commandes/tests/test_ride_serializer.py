from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.commandes.models import FareGrid,Ride
from apps.commandes.serializers import RideCreateSerializer

User = get_user_model()

class RideCreateSerializerTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            email="client.ride@taxigo.test",
            username="client_ride",
            password="TaxiGo1234!",
            phone="+22670001122",
            role="CLIENT",
        )
        self.fare_grid = FareGrid.objects.create(
            pickup_price=Decimal("500.00"),
            price_per_km=Decimal("200.00"),
            active=True,
        )

        self.factory = APIRequestFactory()
        self.request = self.factory.post(
                            "/api/v1/rides/"
                        )
        self.request.user = self.user

    def test_create_ride_successfully(self):
        data = {
            "departure_latitude": 12.371427,
            "departure_longitude": -1.519660,
            "arrival_latitude": 12.402100,
            "arrival_longitude": -1.483000,
        }
        serializer = RideCreateSerializer(
                        data=data,
                        context={"request": self.request}
                    )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors
        )
        ride = serializer.save()
        self.assertEqual(Ride.objects.count(), 1)
        self.assertEqual(ride.passenger, self.user)
        self.assertEqual(
            ride.status,
            Ride.StatusType.WAITING
        )
        self.assertEqual(
            ride.distance_km,
            Decimal("5.243")
        )

        self.assertEqual(
            ride.estimated_price,
            Decimal("1548.60")
        )

    def test_passenger_cannot_create_second_active_ride(self):
        Ride.objects.create(
            passenger =self.user,
            departure_latitude= 12.371427,
            departure_longitude= -1.519660,
            arrival_latitude= 12.402100,
            arrival_longitude= -1.483000,
            distance_km=Decimal("5.000"),
            estimated_price=Decimal("1500.00"),
            status=Ride.StatusType.WAITING,
        )
        data = {
            "departure_latitude": 12.380000,
            "departure_longitude": -1.510000,
            "arrival_latitude": 12.410000,
            "arrival_longitude": -1.470000,
        }
        serializer = RideCreateSerializer(
                        data=data,
                        context={"request": self.request}
                    )
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "You already have an active ride",
            str(serializer.errors)
        )

    def test_passenger_can_create_new_ride_after_completed_ride(self):
        Ride.objects.create(
            passenger=self.user,
            departure_latitude=12.371427,
            departure_longitude=-1.519660,
            arrival_latitude=12.402100,
            arrival_longitude=-1.483000,
            distance_km=Decimal("5.000"),
            estimated_price=Decimal("1500.00"),
            status=Ride.StatusType.COMPLETED,
        )

        data = {
            "departure_latitude": 12.380000,
            "departure_longitude": -1.510000,
            "arrival_latitude": 12.410000,
            "arrival_longitude": -1.470000,
        }

        serializer = RideCreateSerializer(
            data=data,
            context={"request": self.request}
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors
        )

        ride = serializer.save()

        self.assertEqual(Ride.objects.count(), 2)
        self.assertEqual(
            ride.status,
            Ride.StatusType.WAITING
        )