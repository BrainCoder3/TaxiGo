from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from apps.taxis.models import Driver
from apps.commandes.models import Ride


User = get_user_model()


class AvailableRidesTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.passenger = User.objects.create_user(
            email="passenger.available@taxigo.test",
            username="passenger_available",
            password="TaxiGo1234!",
            phone="+22670004001",
            role="CLIENT",
        )

        self.driver_user = User.objects.create_user(
            email="driver.available@taxigo.test",
            username="driver_available",
            password="TaxiGo1234!",
            phone="+22670004002",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-AVAILABLE-001",
            availability_status=Driver.StatusType.AVAILABLE,
        )

        self.waiting_ride = Ride.objects.create(
            passenger=self.passenger,
            departure_latitude=Decimal("12.371427"),
            departure_longitude=Decimal("-1.519660"),
            arrival_latitude=Decimal("12.402100"),
            arrival_longitude=Decimal("-1.483000"),
            distance_km=Decimal("5.243"),
            estimated_price=Decimal("1548.60"),
            status=Ride.StatusType.WAITING,
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

    def test_driver_can_list_available_rides(self):

        response = self.client.get(
            "/api/v1/rides/available/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            str(response.data[0]["id"]),
            str(self.waiting_ride.id)
        )

    def test_accepted_ride_is_not_available(self):

        self.waiting_ride.status = Ride.StatusType.ACCEPTED
        self.waiting_ride.driver = self.driver
        self.waiting_ride.save(
            update_fields=["status", "driver"]
        )

        response = self.client.get(
            "/api/v1/rides/available/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_cancelled_ride_is_not_available(self):

        self.waiting_ride.status = Ride.StatusType.CANCELLED
        self.waiting_ride.save(
            update_fields=["status"]
        )

        response = self.client.get(
            "/api/v1/rides/available/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_passenger_cannot_list_available_rides(self):

        self.client.force_authenticate(
            user=self.passenger
        )

        response = self.client.get(
            "/api/v1/rides/available/"
        )

        self.assertEqual(
            response.status_code,
            403
        )