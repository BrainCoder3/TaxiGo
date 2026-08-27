from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from apps.taxis.models import Driver
from apps.commandes.models import Ride

User = get_user_model()


class RideAcceptTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.passenger = User.objects.create_user(
            email="passenger.accept@taxigo.test",
            username="passenger_accept",
            password="TaxiGo1234!",
            phone="+22670001001",
            role="CLIENT",
        )

        self.driver_user = User.objects.create_user(
            email="driver.accept@taxigo.test",
            username="driver_accept",
            password="TaxiGo1234!",
            phone="+22670001002",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-TEST-ACCEPT-001",
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
            user=self.driver_user
        )

    def test_available_driver_can_accept_ride(self):
        url = f"/api/v1/rides/{self.ride.id}/accept/"

        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.ACCEPTED
        )

        self.assertEqual(
            self.ride.driver,
            self.driver
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.ON_A_RIDE
        )


    def test_unavailable_driver_cannot_accept_ride(self):
        self.driver.availability_status = Driver.StatusType.UNAVAILABLE
        self.driver.save()
        url = f"/api/v1/rides/{self.ride.id}/accept/"
        response = self.client.patch(url)
        self.assertEqual(
            response.status_code,
            400
        )
        self.ride.refresh_from_db()
        self.driver.refresh_from_db()
        self.assertEqual(
            self.ride.status,
            Ride.StatusType.WAITING
        )
        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.UNAVAILABLE
        )
        self.assertIsNone(self.ride.driver)

    def test_already_accepted_ride_cannot_be_accepted_again(self):
        url = f"/api/v1/rides/{self.ride.id}/accept/"

        first_response = self.client.patch(url)

        self.assertEqual(
            first_response.status_code,
            200
        )

        second_response = self.client.patch(url)

        self.assertEqual(
            second_response.status_code,
            404
        )
        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.ACCEPTED
        )

        self.assertEqual(
            self.ride.driver,
            self.driver
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.ON_A_RIDE
        )