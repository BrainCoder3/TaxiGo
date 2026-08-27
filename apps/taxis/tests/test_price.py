from decimal import Decimal
from django.test import SimpleTestCase

from apps.taxis.utils import calculate_price


class CalculatePriceTests(SimpleTestCase):

    def test_zero_km_returns_pickup_price(self):
        price = calculate_price(
            0,
            500,
            200
        )

        self.assertEqual(
            price,
            Decimal("500")
        )

    def test_ten_km_price(self):
        price = calculate_price(
            10,
            500,
            200
        )

        self.assertEqual(
            price,
            Decimal("2500")
        )

    def test_decimal_distance_price(self):
        price = calculate_price(
            2.5,
            500,
            200
        )

        self.assertEqual(
            price,
            Decimal("1000.0")
        )