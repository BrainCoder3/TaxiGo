from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from decimal import Decimal

from apps.commandes.models import Ride
from apps.taxis.models import Driver


User = get_user_model()


class RideConstraintTests(TestCase):

    def setUp(self):
        self.passenger = User.objects.create_user(
            email="constraint.passenger@taxigo.test",
            username="constraint_passenger",
            password="TaxiGo1234!",
            phone="+22670005001",
            role="CLIENT",
        )

        self.driver_user = User.objects.create_user(
            email="constraint.driver@taxigo.test",
            username="constraint_driver",
            password="TaxiGo1234!",
            phone="+22670005002",
            role="DRIVER",
        )

        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="BF-CONSTRAINT-001",
            availability_status=Driver.StatusType.ON_A_RIDE,
        )

    def create_ride(self, **kwargs):
        data = {
            "passenger": self.passenger,
            "departure_latitude": Decimal("12.371427"),
            "departure_longitude": Decimal("-1.519660"),
            "arrival_latitude": Decimal("12.402100"),
            "arrival_longitude": Decimal("-1.483000"),
            "distance_km": Decimal("5.243"),
            "estimated_price": Decimal("1548.60"),
        }

        data.update(kwargs)

        return Ride.objects.create(**data)

    def test_passenger_cannot_have_two_active_rides(self):
        self.create_ride(
            status=Ride.StatusType.WAITING
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_ride(
                    status=Ride.StatusType.WAITING
                )

    def test_driver_cannot_have_two_active_rides(self):
        self.create_ride(
            driver=self.driver,
            status=Ride.StatusType.ACCEPTED,
        )

        other_passenger = User.objects.create_user(
            email="other.constraint@taxigo.test",
            username="other_constraint",
            password="TaxiGo1234!",
            phone="+22670005003",
            role="CLIENT",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_ride(
                    passenger=other_passenger,
                    driver=self.driver,
                    status=Ride.StatusType.IN_PROGRESS,
                )

    def test_passenger_can_have_multiple_completed_rides(self):
        self.create_ride(
            status=Ride.StatusType.COMPLETED
        )

        self.create_ride(
            status=Ride.StatusType.COMPLETED
        )

        self.assertEqual(
            Ride.objects.filter(
                passenger=self.passenger
            ).count(),
            2
        )