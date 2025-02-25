from flask import Blueprint, jsonify, request
from db_config import get_db
from sqlalchemy import text
from services import get_weather_by_coordinate

weather_bp = Blueprint("weather", __name__)

# Get current weather by lat and lon
@weather_bp.route("/weather/current", methods=['GET'])
def get_current_weather():
    """
    API Endpoint: /weather/current
    Method: GET
    
    Description:
    - Fetches real-time weather data for a given latitude (`lat`) and longitude (`lon`)
    - Calls the OpenWeather API to retrieve the latest weather information.

    Example API Request:
    GET api/weather/current?lat=53.3409&lon=-6.2625

    Example Response:
    {
        "clouds": 20,
        "dew_point": 4.76,
        "dt": 1740420079,
        "feels_like": 3.91,
        "humidity": 81,
        "pressure": 1006,
        "sunrise": 1740381840,
        "sunset": 1740419572,
        "temp": 7.81,
        "uvi": 0,
        "visibility": 10000,
        "weather": [
            {
            "description": "few clouds",
            "icon": "02n",
            "id": 801,
            "main": "Clouds"
            }
        ],
        "wind_deg": 230,
        "wind_speed": 7.72
        }


    Returns:
    - 200 OK: JSON list of current weather.
    - 400 Error: Missing parameters.
    - 500 S: OpenWeather API call falir
    """
    params = request.args
    lat = params.get("lat")
    lon = params.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing 'lat' or 'lon' parameters"}), 400

    # Call the OpenWeather API
    result = get_weather_by_coordinate(lat, lon)

    if result.get("status") != 200:
        return jsonify({"error": "Failed to fetch weather data"}), result.get("status", 500)

    return jsonify(result.get("data", {})), 200

# Get historical weather data by lat and lon from database
@weather_bp.route("/weather/historical", methods=["GET"])
def get_historical_weather():
    engine = get_db("weather")
    data = []

    with engine.connect() as conn:
        result = conn.execute(text("SELECT record_date, temp, wind_speed FROM current_data"))
        for row in result:
            row_dict = {
                'date': row[0],
                'temp': row[1],
                'wind_speed': row[2]
            }
            data.append(row_dict)
    
    return jsonify(data=data)
# TODO: discuss what data to store into our database