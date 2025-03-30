import requests
import os
from dotenv import load_dotenv
from flask import jsonify
import datetime

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("BIKE_API_KEY")

def get_all_stations():
    if not API_KEY:
        raise ValueError("Missing Dublin Bike API key.")
    
    res = requests.get('https://api.jcdecaux.com/vls/v1/stations', params={"apiKey": API_KEY, "contract": 'dublin'})

    if res.status_code == 200:
        raw_data = res.json()
        data = []
        for row in raw_data:
            dt = datetime.datetime.fromtimestamp(row['last_update'] / 1000)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

            row_dict = {
                "id": row['number'],
                "name": row['name'],
                "address": row['address'],
                "lat": row['position']['lat'],
                "lon": row['position']['lng'],
                "details": {
                    "status": row['status'],
                    "last_update": formatted_date,
                    "available_bikes": row['available_bikes'],
                    "available_bike_stands": row['available_bike_stands']
                }
            }

            data.append(row_dict)
        
        return {"data": data}
    else:
        return {"status": res.status_code}