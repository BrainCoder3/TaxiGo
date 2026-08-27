from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.taxis.models import Driver, Vehicle


User = get_user_model()


class VehicleAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.driver_user = User.objects.create_user(
            email="vehicle.driver@taxigo.test",
            username="vehicle_driver",
            password="TaxiGo1234!",
            phone="+22672000001",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-VEHICLE-001",
            availability_status=Driver.StatusType.AVAILABLE,
        )

        self.other_driver_user = User.objects.create_user(
            email="vehicle.other@taxigo.test",
            username="vehicle_other",
            password="TaxiGo1234!",
            phone="+22672000002",
            role="DRIVER",
        )

        self.other_driver = Driver.objects.create(
            user=self.other_driver_user,
            license_number="BF-VEHICLE-002",
            availability_status=Driver.StatusType.AVAILABLE,
        )

        self.passenger = User.objects.create_user(
            email="vehicle.passenger@taxigo.test",
            username="vehicle_passenger",
            password="TaxiGo1234!",
            phone="+22672000003",
            role="CLIENT",
        )

        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            brand="Toyota",
            model="Corolla",
            registration_number="11 JK 4587",
            seats=5,
            vehicle_type="SEDAN",
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

    def test_driver_can_create_vehicle(self):
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "brand": "Renault",
                "model": "Clio",
                "registration_number": "22 AB 1234",
                "seats": 5,
                "vehicle_type": "SEDAN",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        vehicle = Vehicle.objects.get(
            registration_number="22 AB 1234"
        )

        self.assertEqual(
            vehicle.driver,
            self.driver
        )

    def test_driver_can_list_only_own_vehicles(self):
        Vehicle.objects.create(
            driver=self.other_driver,
            brand="Peugeot",
            model="208",
            registration_number="33 CD 5678",
            seats=5,
            vehicle_type="SEDAN",
        )

        response = self.client.get(
            "/api/v1/vehicles/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        returned_ids = [
            str(item["id"])
            for item in response.data
        ]

        self.assertIn(
            str(self.vehicle.id),
            returned_ids
        )

        self.assertEqual(
            len(returned_ids),
            1
        )

    def test_other_driver_cannot_retrieve_vehicle(self):
        self.client.force_authenticate(
            user=self.other_driver_user
        )

        response = self.client.get(
            f"/api/v1/vehicles/{self.vehicle.id}/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_other_driver_cannot_update_vehicle(self):
        self.client.force_authenticate(
            user=self.other_driver_user
        )

        response = self.client.patch(
            f"/api/v1/vehicles/{self.vehicle.id}/",
            {
                "brand": "Hacked Brand"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.brand,
            "Toyota"
        )

    def test_passenger_cannot_create_vehicle(self):
        self.client.force_authenticate(
            user=self.passenger
        )

        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "brand": "Toyota",
                "model": "Yaris",
                "registration_number": "44 EF 9999",
                "seats": 5,
                "vehicle_type": "SEDAN",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_registration_number_is_normalized(self):
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "brand": "Toyota",
                "model": "Yaris",
                "registration_number": "  ab 12 cd  ",
                "seats": 5,
                "vehicle_type": "SEDAN",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        vehicle = Vehicle.objects.get(
            registration_number="AB 12 CD"
        )

        self.assertEqual(
            vehicle.registration_number,
            "AB 12 CD"
        )

    def test_vehicle_requires_at_least_one_seat(self):
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "brand": "Toyota",
                "model": "Yaris",
                "registration_number": "ZERO-SEAT",
                "seats": 0,
                "vehicle_type": "SEDAN",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )