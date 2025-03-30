import requests
import os
from db_helper import DBHelper
import datetime
import pandas as pd
from config import Config


class WeatherScraper:
    """
    This class fetches weather data for bike stations using latitude and longitude.
    It stores the raw API response in local files and saves processed data into
    the database for both current and forecast weather conditions.
    """
    
    def __init__(self):
        """Initializes the WeatherScraper with API configuration and database helper."""
        
        # Load weather API configuration
        weather_config = Config().get_weather_config()
        self.weather_api_key = weather_config.weather_api_key
        self.dh = DBHelper()
        self.now = datetime.datetime.now()

    def create_weather_data_folder(self):
        """Creates a folder for storing weather data."""

        if not os.path.exists('weather_data'):
            os.mkdir('weather_data')
            print("Folder 'weather_data' created!")
        else:
            print("Folder 'weather_data' already exists.")

        formatted_now = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        self.subfolder_path = f"weather_data/{formatted_now}"
        os.makedirs(self.subfolder_path, exist_ok=True)

    def write_to_file(self, station_id, lat, lng, response):
        """Writes the weather API response to a file."""
        with open(f"{self.subfolder_path}/weather_{station_id}_{lat}_{lng}", "w") as file:
            file.write(response.text)

    def modify_col_types(self, df):
        if 'sunrise' in df.columns:
            df['sunrise'] = pd.to_datetime(df['sunrise'], unit='s')
            df['sunset'] = pd.to_datetime(df['sunset'], unit='s')
        df['weather'] = df['weather'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {})
        df[['weather_id', 'weather_main', 'weather_description', 'weather_icon']] = pd.json_normalize(df['weather'])
        return df

    def write_to_db_current(self, station_id, lat, lng, weather_data):
        """Processes and writes weather data into the database."""

        current_df = pd.json_normalize(weather_data['current'])
        current_df = self.modify_col_types(current_df)
        current_df['station_id'] = station_id
        current_df['position_lat'] = lat
        current_df['position_lng'] = lng
        current_df['record_time'] = pd.to_datetime(current_df['dt'], unit='s')
        current_df['record_date'] = pd.to_datetime(current_df['dt'], unit='s').dt.date
        current_df['record_hour'] = pd.to_datetime(current_df['dt'], unit='s').dt.hour
        current_cols = ['station_id', 'position_lat', 'position_lng', 'record_time', 'record_date', 'record_hour',
                        'sunrise', 'sunset', 'temp', 'feels_like',
                        'pressure', 'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain_1h', 'snow_1h']
        current_df = current_df.reindex(columns=current_cols).fillna(0)

        self.dh.save_df_data(df=current_df, db_name="weather", table_name="current_data")

    def write_to_db_forecast(self, station_id, lat, lng, weather_data):
        """Processes and writes weather data into the database."""

        hourly_forecast = pd.json_normalize(weather_data['hourly'])
        hourly_forecast = self.modify_col_types(hourly_forecast)
        hourly_forecast['station_id'] = station_id
        hourly_forecast['position_lat'] = lat
        hourly_forecast['position_lng'] = lng
        hourly_forecast['record_time'] = datetime.datetime.now()
        hourly_forecast['record_hourly_time'] = hourly_forecast['record_time'].dt.floor('h')
        hourly_forecast['forecast_hour'] = pd.to_datetime(hourly_forecast['dt'], unit='s')
        hourly_forecast['hours_ahead'] = (hourly_forecast['forecast_hour'] - hourly_forecast['record_hourly_time']).dt.total_seconds() // 3600

        hourly_cols = ['station_id', 'position_lat', 'position_lng', 'record_time', 'record_hourly_time',
                       'hours_ahead', 'forecast_hour', 'temp', 'feels_like', 'pressure',
                       'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain_1h', 'snow_1h']

        hourly_forecast = hourly_forecast.reindex(columns=hourly_cols).fillna(0)
        self.dh.save_df_data(df=hourly_forecast, db_name="weather", table_name="hourly_forecast")

        daily_forecast = pd.json_normalize(weather_data['daily'])
        daily_forecast = self.modify_col_types(daily_forecast)
        daily_forecast['station_id'] = station_id
        daily_forecast['position_lat'] = lat
        daily_forecast['position_lng'] = lng
        daily_forecast['record_time'] = datetime.datetime.now()
        daily_forecast['record_date'] = daily_forecast['record_time'].dt.date
        daily_forecast['forecast_date'] = pd.to_datetime(daily_forecast['dt'], unit='s').dt.date
        daily_forecast['days_ahead'] = (pd.to_datetime(daily_forecast['forecast_date']) - pd.to_datetime(daily_forecast['record_date'])).dt.days
        daily_cols = ['station_id', 'position_lat', 'position_lng', 'record_time', 'record_date', 'forecast_date', 'days_ahead',
                      'sunrise', 'sunset', 'temp_day', 'temp_max', 'temp_min',
                      'feels_like_temp_day', 'feels_like_temp_max', 'feels_like_temp_min',
                      'pressure', 'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain', 'snow']

        daily_forecast = daily_forecast.reindex(columns=daily_cols).fillna(0)
        self.dh.save_df_data(df=daily_forecast, db_name="weather", table_name="daily_forecast")

    def get_station_location(self):
        sql = """
            SELECT
                s.id
                , s.position_lat
                , s.position_lng
            FROM bike.station AS s
        """
        self.station_df = self.dh.query_data(sql)

    def fetch_station_weather(self):
        """Fetches weather data for each station and stores it in a file and database."""

        self.create_weather_data_folder()
        # Iterate over each row in the DataFrame
        for index, row in self.station_df.iterrows():
            station_id, lat, lng = row['id'], row['position_lat'], row['position_lng']

            # Make an API request to OpenWeatherMap
            response = requests.get(
                f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&appid={self.weather_api_key}&units=metric'
            )

            # Process the response
            if response.status_code == 200:
                weather_data = response.json()
                print(f"Weather for Station {row['id']}: {weather_data}")
            else:
                print(f"Failed to fetch weather for Station {row['id']} (Status: {response.status_code})")
            self.write_to_file(station_id, lat, lng, response)
            self.write_to_db_current(station_id, lat, lng, weather_data)
            self.write_to_db_forecast(station_id, lat, lng, weather_data)

    def run(self):
        self.get_station_location()
        self.fetch_station_weather()
