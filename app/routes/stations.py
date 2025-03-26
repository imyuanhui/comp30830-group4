from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db_config import get_db
from services import get_all_stations
from utils import haversine

stations_bp = Blueprint("stations", __name__)


@stations_bp.route("/stations", methods=["GET"])
def get_stations():
    """
    API Endpoint: /api/stations
    Method: GET

    Description:
    - Fetches bike station data and allows filtering based on various parameters.
    - Supports filtering by `id`, `name`, and `address`.
    - Supports proximity filtering to return stations within a given maximum distance (km) 
      from a specified latitude and longitude using the Haversine formula.

    Query Parameters:
    - `id` (int, optional): Filters stations by their unique ID.
    - `name` (str, optional): Filters stations whose names contain the given value (case-insensitive).
    - `address` (str, optional): Filters stations whose addresses contain the given value (case-insensitive).
    - `position_lat` (float, optional): Latitude of the reference location for proximity filtering.
    - `position_lng` (float, optional): Longitude of the reference location for proximity filtering.
    - `maxdist` (float, optional): Maximum distance (in km) within which stations should be returned.
    
      - If `position_lat` and `position_lng` are provided along with `maxdist`, only stations within 
        `maxdist` km of the given coordinates are returned.
      - If `maxdist` is not provided, exact match filtering on `position_lat` and `position_lng` 
        (with a small precision tolerance) is applied instead.

    Example API Request:
    GET /api/stations?position_lat=53.3409&position_lng=-6.2625&maxdist=0.25

    Example Response:
    {
        "data": [
            {
                "address": "York Street East",
                "details": {
                    "available_bike_stands": 23,
                    "available_bikes": 9,
                    "last_update": "2025-03-26 18:27:23",
                    "status": "OPEN"
                },
                "id": 52,
                "lat": 53.338755,
                "lon": -6.262003,
                "name": "YORK STREET EAST"
            },
            {
                "address": "Clarendon Row",
                "details": {
                    "available_bike_stands": 24,
                    "available_bikes": 7,
                    "last_update": "2025-03-26 18:25:19",
                    "status": "OPEN"
                },
                "id": 1,
                "lat": 53.340927,
                "lon": -6.262501,
                "name": "CLARENDON ROW"
            },
            {
                "address": "Exchequer Street",
                "details": {
                    "available_bike_stands": 4,
                    "available_bikes": 20,
                    "last_update": "2025-03-26 18:25:07",
                    "status": "OPEN"
                },
                "id": 9,
                "lat": 53.343034,
                "lon": -6.263578,
                "name": "EXCHEQUER STREET"
            },
            {
                "address": "York Street West",
                "details": {
                    "available_bike_stands": 0,
                    "available_bikes": 0,
                    "last_update": "2025-03-26 18:23:07",
                    "status": "OPEN"
                },
                "id": 51,
                "lat": 53.339334,
                "lon": -6.264699,
                "name": "YORK STREET WEST"
            }
        ]
    }

    Returns:
    - 200 OK: JSON list of bike stations matching the filters.
    - 400 Bad Request: If latitude, longitude, or maxdist values are invalid.
    - 404 Not Found: If no stations match the criteria.
    """
    stations = get_all_stations()['data']
    params = request.args

    # Apply proximity filtering if maxdist, lat and lng are provided
    if "maxdist" in params and "position_lat" in params and "position_lng" in params:
        try:
            user_lat = float(params["position_lat"])
            user_lng = float(params["position_lng"])
            distance = float(params["maxdist"])
            stations = [
                s for s in stations if haversine(user_lat, user_lng, s["lat"], s["lon"]) <= distance
            ]
        except ValueError:
            return jsonify({"error": "Invalid latitude or longitude format"}), 400
    else:
    # Apply basic filtering
        filters = {
            "id": lambda s, v: str(s["id"]) == v,
            "name": lambda s, v: v.lower() in s["name"].lower(),
            "address": lambda s, v: v.lower() in s["address"].lower(),
            "position_lat": lambda s, v: float(v) - 0.0001 <= s["lat"] <= float(v) + 0.0001,
            "position_lng": lambda s, v: float(v) - 0.0001 <= s["lon"] <= float(v) + 0.0001
        }
        for key, filter_func in filters.items():
            if key in params:
                stations = [s for s in stations if filter_func(s, params[key])]

    return jsonify(data=stations)

@stations_bp.route("/stations/history", methods=["GET"])
def get_stations_from_database():
    engine = get_db("bike")
    params = request.args

    # Build dynamic conditions for filtering
    conditions = []
    query_params = {}

    for field, value in params.items():
        if field in ["position_lat", "position_lng"]:  # Handle floating-point values
            conditions.append(f"{field} BETWEEN :{field}_min AND :{field}_max")
            query_params[f"{field}_min"] = float(value) - 0.0001
            query_params[f"{field}_max"] = float(value) + 0.0001
        else:
            conditions.append(f"{field} = :{field}")  # Use named parameters
            query_params[field] = value

    # Construct main station query
    base_query = "SELECT id, name, address, position_lat, position_lng FROM station"
    query = base_query + " WHERE " + " AND ".join(conditions) if conditions else base_query

    data = []
    station_ids = []  # Collect station IDs for batch fetching of details

    with engine.connect() as conn:
        result = conn.execute(text(query), query_params).fetchall()
        for row in result:
            station_id = row[0]
            station_ids.append(station_id)

            data.append({
                'id': station_id,
                'name': row[1],
                'address': row[2],
                'lat': row[3],
                'lon': row[4],
                'details': {}  # Placeholder for availability details
            })

        # Fetch details for all stations in a single query (avoiding multiple queries)
        if station_ids:
            details_query = text("""
                SELECT station_id, status, last_update, available_bikes, available_bike_stands
                FROM availability
                WHERE station_id IN :station_ids
            """)
            details_result = conn.execute(details_query, {'station_ids': tuple(station_ids)}).fetchall()

            # Map availability details to stations
            details_map = {row[0]: {'status': row[1], 'last_update': row[2], 'available_bikes': row[3], 'available_bike_stands': row[4]}
                           for row in details_result}

            # Attach availability details to each station
            for station in data:
                station['details'] = details_map.get(station['id'], {})

    return jsonify(data=data)