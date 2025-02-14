import requests
import os

from db_helper import DBHelper
import datetime
import pandas as pd
from config import Config


class WeatherScraper:
    def __init__(self):
        # latitude and longitude of Dublin
        lat, lon = 53.3476, -6.2637
        weather_config = Config().get_weather_config()
        self.weather_api_key = weather_config.weather_api_key
        self.r = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={weather_config.weather_api_key}&units=metric')
        self.dh = DBHelper()
        self.now = datetime.datetime.now()

    def write_to_file(self):
        if not os.path.exists('weather_data'):
            os.mkdir('weather_data')
            print("Folder 'weather_data' created!")
        else:
            print("Folder 'weather_data' already exists.")

        formatted_now = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"weather_data/weather_{formatted_now}", "w") as file:
            file.write(self.r.text)

    def modify_col_types(self, df):
        if 'sunrise' in df.columns:
            df['sunrise'] = pd.to_datetime(df['sunrise'], unit='s')
            df['sunset'] = pd.to_datetime(df['sunset'], unit='s')
        df['weather'] = df['weather'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {})
        df[['weather_id', 'weather_main', 'weather_description', 'weather_icon']] = pd.json_normalize(df['weather'])
        return df

    def write_to_db(self):
        weather_data = self.r.json()
        current_df = pd.json_normalize(weather_data['current'])
        current_df = self.modify_col_types(current_df)
        current_df['record_time'] = pd.to_datetime(current_df['dt'], unit='s')
        current_df['record_date'] = pd.to_datetime(current_df['dt'], unit='s').dt.date
        current_df['record_hour'] = pd.to_datetime(current_df['dt'], unit='s').dt.hour
        current_cols = ['record_time', 'record_date', 'record_hour', 'sunrise', 'sunset', 'temp', 'feels_like',
                        'pressure', 'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain_1h', 'snow_1h']
        current_df = current_df.reindex(columns=current_cols).fillna(0)

        self.dh.save_df_data(df=current_df, db_name="weather", table_name="current_data")

        hourly_forecast = pd.json_normalize(weather_data['hourly'])
        hourly_forecast = self.modify_col_types(hourly_forecast)
        hourly_forecast['record_time'] = datetime.datetime.now()
        hourly_forecast['record_hourly_time'] = hourly_forecast['record_time'].dt.floor('h')
        hourly_forecast['forecast_hour'] = pd.to_datetime(hourly_forecast['dt'], unit='s')
        hourly_forecast['hours_ahead'] = (hourly_forecast['forecast_hour'] - hourly_forecast['record_hourly_time']).dt.total_seconds() // 3600

        hourly_cols = ['record_time', 'record_hourly_time', 'hours_ahead', 'forecast_hour',
                       'temp', 'feels_like', 'pressure', 'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain_1h', 'snow_1h']

        hourly_forecast = hourly_forecast.reindex(columns=hourly_cols).fillna(0)
        self.dh.save_df_data(df=hourly_forecast, db_name="weather", table_name="hourly_forecast")

        daily_forecast = pd.json_normalize(weather_data['daily'])
        daily_forecast = self.modify_col_types(daily_forecast)
        daily_forecast['record_time'] = datetime.datetime.now()
        daily_forecast['record_date'] = daily_forecast['record_time'].dt.date
        daily_forecast['forecast_date'] = pd.to_datetime(daily_forecast['dt'], unit='s').dt.date
        daily_forecast['days_ahead'] = (pd.to_datetime(daily_forecast['forecast_date']) - pd.to_datetime(daily_forecast['record_date'])).dt.days
        daily_cols = ['record_time', 'record_date', 'forecast_date', 'days_ahead', 'sunrise', 'sunset',
                      'temp_day', 'temp_max', 'temp_min',
                      'feels_like_temp_day', 'feels_like_temp_max', 'feels_like_temp_min',
                      'pressure', 'humidity', 'uvi', 'weather_id', 'wind_speed', 'wind_gust', 'rain', 'snow']

        daily_forecast = daily_forecast.reindex(columns=daily_cols).fillna(0)
        self.dh.save_df_data(df=daily_forecast, db_name="weather", table_name="daily_forecast")

    def run(self):
        if self.r.status_code == 200:
            self.write_to_file()
            self.write_to_db()
        else:
            return self.r.status_code, self.weather_api_key
