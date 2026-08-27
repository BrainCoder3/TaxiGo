from django.test import SimpleTestCase
from apps.taxis.utils import haversine_distance

class HaversineDistanceTests(SimpleTestCase):
    def test_same_coordinates_return_zero(self):
        distance = haversine_distance(
            12.371427,
            -1.519660,
            12.371427,
            -1.519660,
        )
        self.assertEqual(distance,0)

    def test_different_coordinates(self):
        distance = haversine_distance(
                                        0,
                                        0,
                                        0,
                                        1
                                    )
        self.assertAlmostEqual(distance, 111.195,places=3)

    def test_symetrie_coordinates(self):
        distance_ab = haversine_distance(
                                        12.371427,
                                        -1.519660,
                                        12.364200,
                                        -1.533100,
                                    )
        distance_ba = haversine_distance(
                                        12.364200,
                                        -1.533100,
                                        12.371427,
                                        -1.519660,
                                    )
        self.assertAlmostEqual(distance_ab, distance_ba)