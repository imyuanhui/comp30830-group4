from flask import Blueprint, jsonify
from db_config import get_db
from sqlalchemy import text

bikes_bp = Blueprint("bikes", __name__)
            
@bikes_bp.route("/availablebikes/<int:station_id>", methods=["GET"])
def get_bikes_by_station_id(station_id):
    engine = get_db("bike")
    data = []

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT last_update, available_bikes FROM availability WHERE station_id = {station_id}"))
        for row in result:
            row_dict = {
                'time': row[0],
                'available_bikes': row[1],
            }
            data.append(row_dict)
    
    return jsonify(data=data)

@bikes_bp.route("/availablestands/<int:station_id>", methods=["GET"])
def get_stands_by_station_id(station_id):
    engine = get_db("bike")
    data = []

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT last_update, available_bike_stands FROM availability WHERE station_id = {station_id}"))
        for row in result:
            row_dict = {
                'time': row[0],
                'available_stands': row[1],
            }
            data.append(row_dict)
    
    return jsonify(data=data)