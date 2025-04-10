from flask import Blueprint, jsonify, request
from services import get_all_stations, predict_availability
from utils import haversine, filter_nearby_stations
from services import get_weather_by_coordinate_time, get_weather_by_coordinate

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
        # Parse and validate input coordinates
        params = request.args
        start_lat = float(params.get("start_lat"))
        start_lon = float(params.get("start_lon"))
        dest_lat = float(params.get("dest_lat"))
        dest_lon = float(params.get("dest_lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid latitude or longitude values."}), 400

    WALKING_DISTANCE = 0.5  # Maximum walking distance to a bike station

    # Fetch all stations
    stations = get_all_stations()['data']

    # Filter nearby stations based on walking distance
    start_nearby = filter_nearby_stations(stations, start_lat, start_lon, WALKING_DISTANCE)
    dest_nearby = filter_nearby_stations(stations, dest_lat, dest_lon, WALKING_DISTANCE)

    # If `timestamp` is provided, use prediction model for future bike availability
    if "timestamp" in params:
        try:
            timestamp = int(params["timestamp"])

            # Use a central location to get temperature forecast (fallback if specific weather lookup fails)
            central_lat, central_lon = 53.3476, -6.2637
            weather_data = get_weather_by_coordinate_time(central_lat, central_lon, timestamp)["data"]
            temp = weather_data["temp"]

            # Predict availability for start stations
            for station in start_nearby[:]:  # Copy to avoid in-place modification while iterating
                predicted_bikes = int(predict_availability(station["id"], timestamp, temp))
                if predicted_bikes <= 0:
                    start_nearby.remove(station)
                    continue
                station["prediction"] = {"predicted_bike_availability": predicted_bikes}

            # Select the best start station based on proximity
            start_station = min(
                (s for s in start_nearby),
                key=lambda s: haversine(start_lat, start_lon, s["lat"], s["lon"]),
                default=None
            )

            if start_station:
                start_weather = get_weather_by_coordinate_time(start_station["lat"], start_station["lon"], timestamp)["data"]
                start_station["prediction"].update({
                    "temp": start_weather["temp"],
                    "icon": start_weather["icon"],
                    "description": start_weather["description"]
                })

            # Predict availability for destination stations
            for station in dest_nearby[:]:
                predicted_stands = int(predict_availability(station["id"], timestamp, temp, target="stand"))
                if predicted_stands <= 0:
                    dest_nearby.remove(station)
                    continue
                station["prediction"] = {"predicted_stand_availability": predicted_stands}

            # Select best destination station based on distance
            dest_station = min(
                dest_nearby,
                key=lambda s: haversine(dest_lat, dest_lon, s["lat"], s["lon"]),
                default=None
            )

            if dest_station:
                dest_weather = get_weather_by_coordinate_time(dest_station["lat"], dest_station["lon"], timestamp)["data"]
                dest_station["prediction"].update({
                    "temp": dest_weather["temp"],
                    "icon": dest_weather["icon"],
                    "description": dest_weather["description"]
                })

        except Exception as e:
            return jsonify({"error": f"Error while predicting availability: {str(e)}"}), 500
    
    else:
        # Handle real-time availability (no timestamp provided)
        start_station = min(
            (s for s in start_nearby if s["details"]["available_bikes"] > 0),
            key=lambda s: haversine(start_lat, start_lon, s["lat"], s["lon"]),
            default=None
        )

        dest_station = min(
            (s for s in dest_nearby if s["details"]["available_bike_stands"] > 0),
            key=lambda s: haversine(dest_lat, dest_lon, s["lat"], s["lon"]),
            default=None
        )
        
        # Add weather info to start and destination station if available
        if start_station:
            weather = get_weather_by_coordinate(start_station["lat"], start_station["lon"])
            if weather["status"] == 200:
                start_station["prediction"] = {
                    "temp": weather["data"]["temp"],
                    "icon": weather["data"]["weather"][0]["icon"],
                    "description": weather["data"]["weather"][0]["description"]
                }

        if dest_station:
            weather = get_weather_by_coordinate(dest_station["lat"], dest_station["lon"])
            if weather["status"] == 200:
                dest_station["prediction"] = {
                    "temp": weather["data"]["temp"],
                    "icon": weather["data"]["weather"][0]["icon"],
                    "description": weather["data"]["weather"][0]["description"]
                }


    # Handle cases where no suitable stations are found
    if not start_station:
        return jsonify({"error": "No bike stations with enough bikes near the start location."}), 400
    if not dest_station:
        return jsonify({"error": "No bike stations with enough stands near the destination."}), 400

    # Return final recommended stations
    return jsonify({
        "start_station": start_station,
        "destination_station": dest_station
    })