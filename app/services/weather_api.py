import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather():
    if not API_KEY:
        raise ValueError("Missing Openweather API key.")
    
    # latitude and longitude of Dublin
    lat, lon = 53.3476, -6.2637
    res = requests.get('https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&exclude=minutely,hourly,daily,alerts&units=metric')

    if res.status_code == 200:
        data = res.json()
        current_data = data["current"]
        return {
            "weather": current_data["weather"]["main"],
            "temperature": current_data["temp"],
            "wind": current_data["wind_speed"],
            "visibility": current_data["visibility"]
        }
    else:
        return res.status_code, API_KEY

def main():
    weather_data = get_weather()
    print(weather_data)
    # TODO: connect to database

main()

# Things need to be clarified:
# What kind of weather data do we need?
# Time intervals of calling open weather api
# Does the hourly,minutely,daily,alerts data useful for us?