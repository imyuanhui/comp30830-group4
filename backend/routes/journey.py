from flask import Blueprint, jsonify, request
from services import get_all_stations, predict_availability_status
from utils import haversine

journey_bp = Blueprint("journey", __name__)

def filter_nearby_stations(stations, lat, lon, max_distance):
    """Filter stations within the specified max_distance from the given coordinates."""
    return [
        s for s in stations if haversine(lat, lon, s["lat"], s["lon"]) <= max_distance
    ]

@journey_bp.route("/plan-journey", methods=["GET"])
def plan_journey():
    """
    API Endpoint: /api/plan-journey
    Method: GET

    Description:
    - Finds the best bike stations for a journey based on the user's starting point and destination.
    - Filters stations within a walkable distance.
    - Selects the most suitable stations based on bike and slot availability.

    Query Parameters:
    - start_lat (float): Latitude of the starting location.
    - start_lon (float): Longitude of the starting location.
    - dest_lat (float): Latitude of the destination location.
    - dest_lon (float): Longitude of the destination location.
    - timestamp (optional): The timestamp for future journey planning (for bike availability prediction).

    Returns:
    - JSON response with:
        - `start_station`: Nearest station to the starting location with at least 2 bikes available.
        - `destination_station`: Nearest station to the destination with at least 2 empty slots available.
    - Error message if no suitable stations are found.

    Example API Request:
        GET /api/plan-journey?start_lat=53.3559067&start_lon=-6.2581812&dest_lat=53.3489189&dest_lon=-6.2612181&timestamp=1744108800

    Example Response:
        {
            "destination_station": {
                "address": "Princes Street / O'Connell Street",
                "details": {
                "available_bike_stands": 12,
                "available_bikes": 11,
                "last_update": "2025-03-26 19:36:39",
                "status": "OPEN"
                },
                "id": 33,
                "lat": 53.349013,
                "lon": -6.260311,
                "name": "PRINCES STREET / O'CONNELL STREET"
            },
            "start_station": {
                "address": "Mountjoy Square West",
                "details": {
                "available_bike_stands": 9,
                "available_bikes": 21,
                "last_update": "2025-03-26 19:32:26",
                "status": "OPEN"
                },
                "id": 28,
                "lat": 53.356299,
                "lon": -6.258586,
                "name": "MOUNTJOY SQUARE WEST"
            }
        }
    """
    try:
        # Extract query parameters
        params = request.args
        start_lat = float(params.get("start_lat"))
        start_lon = float(params.get("start_lon"))
        dest_lat = float(params.get("dest_lat"))
        dest_lon = float(params.get("dest_lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid latitude or longitude values."}), 400

    # Define walkable distance (in km)
    WALKING_DISTANCE = 0.5  # 0.5 km walkable distance

    # Get all stations
    stations = get_all_stations()['data']

    # Filter nearby stations based on walking distance
    start_nearby = filter_nearby_stations(stations, start_lat, start_lon, WALKING_DISTANCE)
    dest_nearby = filter_nearby_stations(stations, dest_lat, dest_lon, WALKING_DISTANCE)

    # If `timestamp` is provided, use prediction model for future bike availability
    if "timestamp" in params:
        try:
            for s in start_nearby[:]:  # Copy the list to avoid modifying it while iterating
                if predict_availability_status(s["id"], params["timestamp"]) != "sufficient":
                    start_nearby.remove(s)

            # Select the best start station based on proximity
            start_station = min(
                (s for s in start_nearby),
                key=lambda s: haversine(start_lat, start_lon, s["lat"], s["lon"]),
                default=None
            )

            dest_station = min(
                (s for s in dest_nearby),
                key=lambda s: haversine(dest_lat, dest_lon, s["lat"], s["lon"]),
                default=None
            )
        except Exception as e:
            return jsonify({"error": f"Error while predicting availability: {str(e)}"}), 500
    else:
        # Select the best start station with at least 2 bikes
        start_station = min(
            (s for s in start_nearby if s["details"]["available_bikes"] >= 2),
            key=lambda s: haversine(start_lat, start_lon, s["lat"], s["lon"]),
            default=None
        )

        # Select the best destination station with at least 2 available slots
        dest_station = min(
            (s for s in dest_nearby if s["details"]["available_bike_stands"] >= 2),
            key=lambda s: haversine(dest_lat, dest_lon, s["lat"], s["lon"]),
            default=None
        )

    # Return error if no suitable start station or destination station found
    if not start_station:
        return jsonify({"error": "No bike stations with enough bikes near the start location."}), 400
    if not dest_station:
        return jsonify({"error": "No bike stations with enough slots near the destination."}), 400

    # Return the best start and destination station
    return jsonify({
        "start_station": start_station,
        "destination_station": dest_station
    })