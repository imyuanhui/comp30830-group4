# Get filtered stations
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db_config import get_db

stations_bp = Blueprint("stations", __name__)


@stations_bp.route("/stations", methods=["GET"])
def get_stations():
    """
    API Endpoint: /api/stations
    Method: GET

    Description:
    - Fetches bike station data based on provided filters.
    - Supports filtering by `id`, `name`, `address`, `position_lat`, and `position_lng`.
    - Handles floating-point precision for `position_lat` and `position_lng`.
    - Also fetches real-time availability details for each station.

    Example API Request:
    GET /api/stations?name=CLARENDON%20ROW&position_lat=53.3409

    Example Response:
    {
        "data": [
            {
                "id": 1,
                "name": "CLARENDON ROW",
                "address": "Clarendon Row",
                "lat": 53.3409,
                "lon": -6.2625,
                "details": {
                    "status": "OPEN",
                    "last_update": "2024-02-24 14:30:00",
                    "available_bikes": 5,
                    "available_bike_stands": 10
                }
            }
        ]
    }

    Returns:
    - 200 OK: JSON list of matching bike stations with availability details.
    - 404 Not Found: If no stations match the criteria.
    """

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
