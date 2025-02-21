from flask import Blueprint, jsonify
from db_config import get_db
from sqlalchemy import text

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/historicalweather", methods=["GET"])
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