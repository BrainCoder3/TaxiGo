from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from apps.taxis.models import Driver
from apps.commandes.models import Ride


User = get_user_model()


class RideCancelTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.passenger = User.objects.create_user(
            email="passenger.cancel@taxigo.test",
            username="passenger_cancel",
            password="TaxiGo1234!",
            phone="+22670003001",
            role="CLIENT",
        )

        self.other_passenger = User.objects.create_user(
            email="other.passenger@taxigo.test",
            username="other_passenger",
            password="TaxiGo1234!",
            phone="+22670003002",
            role="CLIENT",
        )

        self.driver_user = User.objects.create_user(
            email="driver.cancel@taxigo.test",
            username="driver_cancel",
            password="TaxiGo1234!",
            phone="+22670003003",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-TEST-CANCEL-001",
            availability_status=Driver.StatusType.AVAILABLE,
        )

        self.ride = Ride.objects.create(
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
            user=self.passenger
        )

    def test_passenger_can_cancel_waiting_ride(self):
        url = f"/api/v1/rides/{self.ride.id}/cancel/"

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.ride.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.CANCELLED
        )

        self.assertIsNone(
            self.ride.driver
        )

    def test_passenger_can_cancel_accepted_ride(self):
        self.ride.status = Ride.StatusType.ACCEPTED
        self.ride.driver = self.driver
        self.ride.save(
            update_fields=["status", "driver"]
        )

        self.driver.availability_status = Driver.StatusType.ON_A_RIDE
        self.driver.save(
            update_fields=["availability_status"]
        )

        url = f"/api/v1/rides/{self.ride.id}/cancel/"

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.CANCELLED
        )

        self.assertEqual(
            self.ride.driver,
            self.driver
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.AVAILABLE
        )

    def test_passenger_cannot_cancel_in_progress_ride(self):
        self.ride.status = Ride.StatusType.IN_PROGRESS
        self.ride.driver = self.driver
        self.ride.save(
            update_fields=["status", "driver"]
        )

        self.driver.availability_status = Driver.StatusType.ON_A_RIDE
        self.driver.save(
            update_fields=["availability_status"]
        )

        url = f"/api/v1/rides/{self.ride.id}/cancel/"

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            400
        )

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.IN_PROGRESS
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.ON_A_RIDE
        )

    def test_other_passenger_cannot_cancel_ride(self):
        self.client.force_authenticate(
            user=self.other_passenger
        )

        url = f"/api/v1/rides/{self.ride.id}/cancel/"

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            404
        )

        self.ride.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.WAITING
        )