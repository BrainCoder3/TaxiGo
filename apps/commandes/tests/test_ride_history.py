from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from apps.commandes.models import Ride
from apps.taxis.models import Driver


User = get_user_model()


class RideHistoryTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.passenger1 = User.objects.create_user(
            email="history.p1@taxigo.test",
            username="history_p1",
            password="TaxiGo1234!",
            phone="+22674000001",
            role="CLIENT",
        )

        self.passenger2 = User.objects.create_user(
            email="history.p2@taxigo.test",
            username="history_p2",
            password="TaxiGo1234!",
            phone="+22674000002",
            role="CLIENT",
        )

        self.driver_user = User.objects.create_user(
            email="history.driver@taxigo.test",
            username="history_driver",
            password="TaxiGo1234!",
            phone="+22674000003",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-HISTORY-001",
            availability_status=Driver.StatusType.AVAILABLE,
        )

        self.ride1 = self.create_ride(
            passenger=self.passenger1,
            status=Ride.StatusType.COMPLETED,
            driver=self.driver,
        )

        self.ride2 = self.create_ride(
            passenger=self.passenger2,
            status=Ride.StatusType.COMPLETED,
        )

    def create_ride(self, passenger, status, driver=None):
        return Ride.objects.create(
            passenger=passenger,
            driver=driver,
            departure_latitude=Decimal("12.371427"),
            departure_longitude=Decimal("-1.519660"),
            arrival_latitude=Decimal("12.402100"),
            arrival_longitude=Decimal("-1.483000"),
            distance_km=Decimal("5.243"),
            estimated_price=Decimal("1548.60"),
            status=status,
        )

    def test_passenger_sees_only_own_rides(self):
        self.client.force_authenticate(
            user=self.passenger1
        )

        response = self.client.get(
            "/api/v1/rides/"
        )

        self.assertEqual(response.status_code, 200)

        ids = [
            str(ride["id"])
            for ride in response.data
        ]

        self.assertIn(
            str(self.ride1.id),
            ids
        )

        self.assertNotIn(
            str(self.ride2.id),
            ids
        )

    def test_passenger_cannot_retrieve_other_passenger_ride(self):
        self.client.force_authenticate(
            user=self.passenger1
        )

        response = self.client.get(
            f"/api/v1/rides/{self.ride2.id}/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_driver_sees_only_assigned_rides(self):
        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.get(
            "/api/v1/rides/"
        )

        self.assertEqual(response.status_code, 200)

        ids = [
            str(ride["id"])
            for ride in response.data
        ]

        self.assertIn(
            str(self.ride1.id),
            ids
        )

        self.assertNotIn(
            str(self.ride2.id),
            ids
        )

    def test_driver_cannot_retrieve_unassigned_ride(self):
        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.get(
            f"/api/v1/rides/{self.ride2.id}/"
        )

        self.assertEqual(
            response.status_code,
            404
        )