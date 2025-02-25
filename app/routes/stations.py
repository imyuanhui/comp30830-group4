from flask import Blueprint, jsonify, request
from db_config import get_db
from sqlalchemy import text

stations_bp = Blueprint("stations", __name__)

# Get filtered stations
@stations_bp.route("/stations", methods = ["GET"])
def get_stations():
    """
    API Endpoint: /api/stations
    Method: GET
    
    Description:
    - Fetches bike station data based on provided filters.
    - Supports filtering by `id`, `name`, `address`, `position_lat`, and `position_lng`.
    - Handles floating-point precision for `position_lat` and `position_lng`.

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
                "lon": -6.2625
            }
        ]
    }

    Returns:
    - 200 OK: JSON list of matching bike stations.
    - 404 Not Found: If no stations match the criteria.
    """
    engine = get_db("bike")
    # Get parameters
    params = request.args
    
    # Build dynamic conditions and parameters
    conditions = []
    query_params = {}
    for field, value in params.items():
        if field in ["position_lat", "position_lng"]:  # Handle floating-point fields
            conditions.append(f"{field} BETWEEN :{field}_min AND :{field}_max")
            query_params[f"{field}_min"] = float(value) - 0.0001
            query_params[f"{field}_max"] = float(value) + 0.0001
        else:
            conditions.append(f"{field} = :{field}")  # Use named parameters
            query_params[field] = value
    
    base_query = "SELECT id, name, address, position_lat, position_lng FROM station"
    if conditions:
        query = base_query + " WHERE " + " AND ".join(conditions)
    else:
        query = base_query
    
    data = []
    with engine.connect() as conn:
        result = conn.execute(text(query), query_params)
        for row in result:
            row_dict = {
                'id': row[0],
                'name': row[1],
                'address': row[2],
                'lat': row[3],
                'lon': row[4]
            }
            data.append(row_dict)
    
    return jsonify(data=data)

