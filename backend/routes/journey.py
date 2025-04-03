from flask import Blueprint, jsonify, request
from services import get_all_stations, predict_availability_status
from utils import haversine

journey_bp = Blueprint("journey", __name__)

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

        Returns:
        - JSON response with:
        - `start_station`: Nearest station to the starting location with at least 2 bikes available.
        - `destination_station`: Nearest station to the destination with at least 2 empty slots available.
        - If no suitable stations are found, returns an error message with a 400 status code.

        Example API Request:
        GET api/plan-journey?start_lat=53.3559067&start_lon=-6.2581812&dest_lat=53.3489189&dest_lon=-6.2612181

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
    stations = get_all_stations()['data']
    params = request.args
    start_lat, start_lon, dest_lat, dest_lon = float(params["start_lat"]), float(params["start_lon"]), float(params["dest_lat"]), float(params["dest_lon"])
    WALKING_DISTANCE = 1
    # Filter stations within walking distance
    start_nearby = [
        s for s in stations if haversine(start_lat, start_lon, s["lat"], s["lon"]) <= WALKING_DISTANCE
    ]
    dest_nearby = [
        s for s in stations if haversine(dest_lat, dest_lon, s["lat"], s["lon"]) <= WALKING_DISTANCE
    ]

    # Select the best start station (at least 2 bikes)
    start_station = min(
        (s for s in start_nearby if s["details"]["available_bikes"] >= 2),
        key=lambda s: haversine(start_lat, start_lon, s["lat"], s["lon"]),
        default=None
    )

    # Select the best destination station (at least 2 slots)
    dest_station = min(
        (s for s in dest_nearby if s["details"]["available_bike_stands"] >= 2),
        key=lambda s: haversine(dest_lat, dest_lon, s["lat"], s["lon"]),
        default=None
    )

    if not start_station:
        return jsonify({"error": "No bike stations with enough bikes near the start location."}), 400
    if not dest_station:
        return jsonify({"error": "No bike stations with enough slots near the destination."}), 400

    return jsonify({
        "start_station": start_station,
        "destination_station": dest_station
    })


@journey_bp.route("/plan-journey/future", methods=["GET"])
def plan_future_journey():
    station_id = request.args.get("station_id")
    timestamp = request.args.get("timestamp")  # Todo: confirm the format of timestamp with frontend

    if not station_id or not timestamp:
        return jsonify({"error": "Missing station_id or timestamp"}), 400

    try:
        res = predict_availability_status(station_id, timestamp)

        return jsonify({
            "station_id": station_id,
            "timestamp": timestamp,
            "sufficient": res
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
