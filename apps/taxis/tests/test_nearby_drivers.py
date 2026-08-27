from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from decimal import Decimal

from apps.taxis.models import Driver


User = get_user_model()


class NearbyDriversTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Passager positionné autour de 0,0 pour rendre
        # les distances très faciles à prévoir.
        self.passenger = User.objects.create_user(
            email="passenger.nearby@taxigo.test",
            username="passenger_nearby",
            password="TaxiGo1234!",
            phone="+22671000001",
            role="CLIENT",
        )

        # Chauffeur proche : environ 1.1 km
        self.near_user = User.objects.create_user(
            email="near.driver@taxigo.test",
            username="near_driver",
            password="TaxiGo1234!",
            phone="+22671000002",
            role="DRIVER",
        )

        self.near_driver = Driver.objects.create(
            user=self.near_user,
            license_number="NEAR-001",
            availability_status=Driver.StatusType.AVAILABLE,
            latitude=Decimal("0.000000"),
            longitude=Decimal("0.010000"),
        )

        # Chauffeur intermédiaire : environ 3.3 km
        self.middle_user = User.objects.create_user(
            email="middle.driver@taxigo.test",
            username="middle_driver",
            password="TaxiGo1234!",
            phone="+22671000003",
            role="DRIVER",
        )

        self.middle_driver = Driver.objects.create(
            user=self.middle_user,
            license_number="MIDDLE-001",
            availability_status=Driver.StatusType.AVAILABLE,
            latitude=Decimal("0.000000"),
            longitude=Decimal("0.030000"),
        )

        # Chauffeur plus éloigné : environ 6.7 km
        self.far_user = User.objects.create_user(
            email="far.driver@taxigo.test",
            username="far_driver",
            password="TaxiGo1234!",
            phone="+22671000004",
            role="DRIVER",
        )

        self.far_driver = Driver.objects.create(
            user=self.far_user,
            license_number="FAR-001",
            availability_status=Driver.StatusType.AVAILABLE,
            latitude=Decimal("0.000000"),
            longitude=Decimal("0.060000"),
        )

        # Très proche mais indisponible :
        # il ne doit JAMAIS apparaître.
        self.unavailable_user = User.objects.create_user(
            email="unavailable.driver@taxigo.test",
            username="unavailable_driver",
            password="TaxiGo1234!",
            phone="+22671000005",
            role="DRIVER",
        )

        self.unavailable_driver = Driver.objects.create(
            user=self.unavailable_user,
            license_number="UNAVAILABLE-001",
            availability_status=Driver.StatusType.UNAVAILABLE,
            latitude=Decimal("0.000000"),
            longitude=Decimal("0.001000"),
        )

        self.client.force_authenticate(
            user=self.passenger
        )

    def test_nearby_drivers_are_sorted_by_distance(self):
        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "0.000000",
                "lon": "0.000000",
            },
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            3
        )

        self.assertEqual(
            str(response.data[0]["id"]),
            str(self.near_driver.id)
        )

        self.assertEqual(
            str(response.data[1]["id"]),
            str(self.middle_driver.id)
        )

        self.assertEqual(
            str(response.data[2]["id"]),
            str(self.far_driver.id)
        )

    def test_unavailable_driver_is_not_returned(self):
        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "0.000000",
                "lon": "0.000000",
            },
        )

        returned_ids = [
            str(item["id"])
            for item in response.data
        ]

        self.assertNotIn(
            str(self.unavailable_driver.id),
            returned_ids
        )

    def test_limit_restricts_number_of_results(self):
        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "0.000000",
                "lon": "0.000000",
                "limit": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            2
        )

        self.assertEqual(
            str(response.data[0]["id"]),
            str(self.near_driver.id)
        )

        self.assertEqual(
            str(response.data[1]["id"]),
            str(self.middle_driver.id)
        )

    def test_radius_filters_far_drivers(self):
        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "0.000000",
                "lon": "0.000000",
                "radius": "2.00",
            },
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
            str(self.near_driver.id)
        )

    def test_invalid_latitude_is_rejected(self):
        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "120.000000",
                "lon": "0.000000",
            },
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_driver_cannot_use_nearby_endpoint(self):
        self.client.force_authenticate(
            user=self.near_user
        )

        response = self.client.get(
            "/api/v1/drivers/nearby/",
            {
                "lat": "0.000000",
                "lon": "0.000000",
            },
        )

        self.assertEqual(
            response.status_code,
            403
        )