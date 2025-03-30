import requests
import os
from dotenv import load_dotenv
from flask import jsonify
import datetime

# Load environment variables from .env file
load_dotenv()

# Retrieve the Dublin Bike API key from environment variables
API_KEY = os.getenv("BIKE_API_KEY")

def get_all_stations():
    """
    Fetches real-time Dublin bike station data from the JCDecaux API.

    Returns:
    - dict: A dictionary containing a list of bike stations with their details
      if the request is successful. Otherwise, returns a dictionary with the status code.
    """

    # Check if the API key is available, raise an error if missing
    if not API_KEY:
        raise ValueError("Missing Dublin Bike API key.")
    
    res = requests.get('https://api.jcdecaux.com/vls/v1/stations', params={"apiKey": API_KEY, "contract": 'dublin'})

    # If the request is successful (status code 200), process the data
    if res.status_code == 200:
        raw_data = res.json()
        data = []

        # Loop through each station's data and format it
        for row in raw_data:
            # Convert the timestamp from milliseconds to a human-readable datetime format
            dt = datetime.datetime.fromtimestamp(row['last_update'] / 1000)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

            # Structure the station data in a dictionary
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

            # Append formatted data to the list
            data.append(row_dict)

        # Return the formatted station data
        return {"data": data}
    else:
        # If the request fails, return only the status code
        return {"status": res.status_code}