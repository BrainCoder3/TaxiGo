from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from apps.taxis.models import Driver
from apps.commandes.models import Ride


User = get_user_model()


class RideStatusTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        
        self.passenger = User.objects.create_user(
            email="passenger.status@taxigo.test",
            username="passenger_status",
            password="TaxiGo1234!",
            phone="+22670002001",
            role="CLIENT",
        )

        
        self.driver_user = User.objects.create_user(
            email="driver.status@taxigo.test",
            username="driver_status",
            password="TaxiGo1234!",
            phone="+22670002002",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-TEST-STATUS-001",
            availability_status=Driver.StatusType.ON_A_RIDE,
        )

       
        self.ride = Ride.objects.create(
            passenger=self.passenger,
            driver=self.driver,
            departure_latitude=Decimal("12.371427"),
            departure_longitude=Decimal("-1.519660"),
            arrival_latitude=Decimal("12.402100"),
            arrival_longitude=Decimal("-1.483000"),
            distance_km=Decimal("5.243"),
            estimated_price=Decimal("1548.60"),
            status=Ride.StatusType.ACCEPTED,
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

    def test_driver_can_start_accepted_ride(self):
        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.IN_PROGRESS
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
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

    def test_driver_can_complete_in_progress_ride(self):
        
        self.ride.status = Ride.StatusType.IN_PROGRESS
        self.ride.save(
            update_fields=["status"]
        )

        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.COMPLETED
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.COMPLETED
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.AVAILABLE
        )

    def test_driver_cannot_skip_in_progress_status(self):
        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.COMPLETED
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.ACCEPTED
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.ON_A_RIDE
        )

    def test_completed_ride_cannot_change_status_again(self):
        self.ride.status = Ride.StatusType.COMPLETED
        self.ride.save(
            update_fields=["status"]
        )

        self.driver.availability_status = Driver.StatusType.AVAILABLE
        self.driver.save(
            update_fields=["availability_status"]
        )

        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.IN_PROGRESS
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.ride.refresh_from_db()
        self.driver.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.COMPLETED
        )

        self.assertEqual(
            self.driver.availability_status,
            Driver.StatusType.AVAILABLE
        )

    def test_passenger_cannot_update_ride_status(self):
        self.client.force_authenticate(
            user=self.passenger
        )

        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.IN_PROGRESS
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            403
        )

        self.ride.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.ACCEPTED
        )

    def test_other_driver_cannot_update_ride_status(self):
        other_driver_user = User.objects.create_user(
            email="other.driver@taxigo.test",
            username="other_driver",
            password="TaxiGo1234!",
            phone="+22670002003",
            role="DRIVER",
        )

        Driver.objects.create(
            user=other_driver_user,
            license_number="BF-TEST-STATUS-002",
            availability_status=Driver.StatusType.ON_A_RIDE,
        )

        self.client.force_authenticate(
            user=other_driver_user
        )

        url = f"/api/v1/rides/{self.ride.id}/status/"

        response = self.client.patch(
            url,
            {
                "status": Ride.StatusType.IN_PROGRESS
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.ride.refresh_from_db()

        self.assertEqual(
            self.ride.status,
            Ride.StatusType.ACCEPTED
        )