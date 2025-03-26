from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two latitude/longitude points 
    using the Haversine formula.

    Parameters:
    - lat1, lon1: Latitude and longitude of the first point (in decimal degrees).
    - lat2, lon2: Latitude and longitude of the second point (in decimal degrees).

    Returns:
    - Distance between the two points in kilometers.

    Formula Explanation:
    - Converts latitude and longitude from degrees to radians.
    - Computes the differences in latitude and longitude.
    - Applies the Haversine formula to calculate the central angle.
    - Uses Earth's radius (approx. 6371 km) to compute the distance.
    """
    R = 6371  # Earth's radius in kilometers

    # Convert latitude and longitude from degrees to radians
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    # Apply Haversine formula
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Distance in kilometers
