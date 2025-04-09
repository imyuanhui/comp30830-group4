import requests
import os
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenWeather API key from environment variables
API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather_by_coordinate(lat=53.3476, lon=-6.2637):
    """
    Fetches the current weather data for a given latitude and longitude
    using the OpenWeather API.

    Parameters:
    - lat (float): Latitude of the location (default is Dublin, Ireland).
    - lon (float): Longitude of the location (default is Dublin, Ireland).

    Returns:
    - dict: A dictionary containing the weather status code and current weather data 
      if the request is successful; otherwise, it returns only the status code.
    """

    # Check if the API key is available, raise an error if missing
    if not API_KEY:
        raise ValueError("Missing Openweather API key.")
    
    # Make a request to the OpenWeather API for current weather data
    res = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&exclude=minutely,hourly,daily,alerts&units=metric')

    # If the request is successful (status code 200), return the current weather data
    if res.status_code == 200:
        data = res.json()
        current_data = data["current"]
        return {
            "status": res.status_code,
            "data": current_data
        }
    else:
        # If the request fails, return only the status code
        return {"status": res.status_code}

def get_weather_by_coordinate_time(lat=53.3476,lon=-6.2637,timestamp=1744108800):
    # Check if the API key is available, raise an error if missing
    if not API_KEY:
        raise ValueError("Missing Openweather API key.")
    
    # Make a request to the OpenWeather API for current weather data
    res = requests.get(f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={API_KEY}&units=metric')

    # If the request is successful (status code 200), return the current weather data
    if res.status_code == 200:
        data = res.json()["data"][0]
        print(data)
        temp = data["temp"]
        icon = data["weather"][0]["icon"]
        print(temp, icon)
        return {
            "status": res.status_code,
            "data": {"temp": temp, "icon": icon}
        }
    else:
        # If the request fails, return only the status code
        return {"status": res.status_code}
    