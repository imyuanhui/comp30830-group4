from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db_config import get_db
from services import get_all_stations
from utils import haversine
from datetime import datetime

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

@stations_bp.route("/stations/history/<int:station_id>", methods=["GET"])
def get_station_history_by_id(station_id):
    """
    Endpoint:
        GET /stations/history/<int:station_id>

    API Endpoint: /api/stations/history/<int:station_id>
    Method: GET

    Description:
    - Retrieve the historical bike availability and bike stands availability for a given station (identified by station_id) within a specified time range. 
    - Filters the results by providing a start_time and end_time in the YYYY-MM-DD HH:MM:SS format. 
    - If no time range is provided, all historical records for the station will be returned.
    
    Parameters:
        - `station_id` (int, required): The unique ID of the bike station.
        - `start_time` (optional): The start time for filtering the availability history. Should be in the YYYY-MM-DD HH:MM:SS format (e.g., 2025-02-17 13:00:00). If not provided, no lower bound for the time will be applied.
        - `end_time` (optional): The end time for filtering the availability history. Should be in the YYYY-MM-DD HH:MM:SS format (e.g., 2025-02-17 14:00:00). If not provided, no upper bound for the time will be applied.
    
    Example API Request:
    GET /api/stations/history/1?start_time=2025-02-17 16:00:00&end_time=2025-02-17 16:50:00

    Example Response:
    {
        "data": [
            {
                "available_bike_stands": 19,
                "available_bikes": 12,
                "last_update": "Mon, 17 Feb 2025 16:44:17 GMT"
            }
        ]
    }
    """
    engine = get_db("bike")
    history = []

    # Get query parameters for time range
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')

    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None
    except ValueError:
        return jsonify({"error": "Invalid time format. Expected format: YYYY-MM-DD HH:MM:SS."}), 400
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT available_bikes, available_bike_stands, last_update 
            FROM availability 
            WHERE station_id = :station_id
            ORDER BY last_update ASC
        """), {"station_id": station_id}).fetchall()

        history = []
        for row in result:
            last_update = row[2]
            last_update = datetime.strptime(str(last_update), "%Y-%m-%d %H:%M:%S")

            if (start_time and last_update < start_time) or (end_time and last_update > end_time):
                continue
            history.append({
                    "available_bikes": row[0],
                    "available_bike_stands": row[1],
                    "last_update": row[2]
                })

    return jsonify(data=history)


@stations_bp.route("/stations/history/demo/<int:station_id>", methods=["GET"])
def get_station_history_demo_by_id(station_id):
    """
    Endpoint:
        GET /stations/history/hourly/<int:station_id>

    Description:
    - Retrieve the hourly aggregated bike and bike stand availability for a given station.
    - Currently this is based on **static demo data** for the date `2025-02-23` only.
    - In a real implementation, the time window should dynamically cover the past 24 hours.

    Parameters:
        - `station_id` (int, required): The ID of the bike station.

    Example Request:
        GET /stations/history/hourly/1

    Example Response:
    {
        "data": [
            {
                "record_hour": "2025-02-23 14",
                "station_id": 1,
                "available_bikes": 10,
                "available_bike_stands": 5
            },
            {
                "record_hour": "2025-02-23 15",
                "station_id": 1,
                "available_bikes": 8,
                "available_bike_stands": 7
            },
            ...
        ]
    }
    """
    engine = get_db("bike")
    history = []

    # Note: This query is based on demo data, limited to a fixed 24-hour period (Feb 23, 2025).

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                DATE_FORMAT(record_time, '%Y-%m-%d %H') AS record_hour,
                station_id,
                ROUND(AVG(available_bikes)) AS avg_available_bikes,
                ROUND(AVG(available_bike_stands)) AS avg_available_bike_stands
            FROM bike.availability 
            WHERE station_id = :station_id
              AND record_time BETWEEN '2025-02-23 00:00:00' AND '2025-02-23 23:59:59'
            GROUP BY 1, 2;
        """), {"station_id": station_id}).fetchall()

        # Assemble result as JSON-serializable dictionary
        for row in result:
            history.append({
                "record_hour": row[0],
                "station_id": row[1],
                "available_bikes": row[2],
                "available_bike_stands": row[3]
            })

    return jsonify(data=history)