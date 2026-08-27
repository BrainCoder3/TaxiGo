import math
from decimal import Decimal

def haversine_distance(lat1, lon1, lat2, lon2):
    EARTH_RADIUS_KM = 6371.0

    lat1_radiant = math.radians(lat1)
    lat2_radiant = math.radians(lat2)
    lon1_radiant = math.radians(lon1)
    lon2_radiant = math.radians(lon2)

    delta_lat = lat2_radiant - lat1_radiant
    delta_lon = lon2_radiant - lon1_radiant

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_radiant)
        * math.cos(lat2_radiant)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distance = EARTH_RADIUS_KM * c

    return distance


def calculate_price(distance_km, pickup_price, price_per_km):
    distance_km = Decimal(str(distance_km))
    pickup_price = Decimal(str(pickup_price))
    price_per_km = Decimal(str(price_per_km))

    total_price = pickup_price + price_per_km * distance_km

    return total_price