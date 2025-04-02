from db_helper import DBHelper
import os
import pandas as pd

class DBSetUp:
    def __init__(self):
        self.dh = DBHelper()

    def create_bike_database(self):
        # Create a database for bike-related data
        # https://developer.jcdecaux.com/#/opendata/vls?page=dynamic
        self.dh.create_database(db_name="bike")

    def create_bike_station(self):
        sql = """
            CREATE TABLE bike.station (
                id INTEGER NOT NULL COMMENT 'Station ID (Dublin)',
                name VARCHAR(128) NOT NULL COMMENT 'Station name',
                address VARCHAR(128) NOT NULL COMMENT 'Station address',
                position_lat FLOAT NOT NULL COMMENT 'Latitude',
                position_lng FLOAT NOT NULL COMMENT 'Longitude',
                PRIMARY KEY (id)
            );
            """
        self.dh.create_table(sql=sql, table_name="bike.station")

    def create_bike_availability(self):
        sql = """
        CREATE TABLE bike.availability (
            station_id INTEGER NOT NULL COMMENT 'Station ID (Dublin)',
            status VARCHAR(128) NOT NULL COMMENT 'Status (CLOSED/OPEN)',
            available_bikes INTEGER NOT NULL COMMENT 'Available bikes',
            available_bike_stands INTEGER NOT NULL COMMENT 'Available bike stands',
            last_update DATETIME NOT NULL COMMENT 'Last update time',
            record_time DATETIME NOT NULL COMMENT 'Data record time',
            PRIMARY KEY (station_id, record_time)
            );
        """
        self.dh.create_table(sql=sql, table_name="bike.availability")

    def create_weather_schema(self):
        # Create a database for weather-related data
        # https://openweathermap.org/api/one-call-3
        self.dh.create_database(db_name="weather")

    def create_weather_current_date(self):
        sql = """
        CREATE TABLE weather.current_data (
            station_id INTEGER NOT NULL COMMENT 'Station ID (Dublin)',
            position_lat FLOAT NOT NULL COMMENT 'Station latitude',
            position_lng FLOAT NOT NULL COMMENT 'Station longitude',
            record_time DATETIME NOT NULL COMMENT 'Data record time',
            record_date DATE NOT NULL COMMENT 'Data record date',
            record_hour INTEGER NOT NULL COMMENT 'Data record hour (0-23)',
            sunrise DATETIME NOT NULL COMMENT 'Sunrise time',
            sunset DATETIME NOT NULL COMMENT 'Sunset time',
            temp FLOAT NOT NULL COMMENT 'Temperature (Celsius)',
            feels_like FLOAT NOT NULL COMMENT 'Feels like temperature (Celsius)',
            pressure INTEGER NOT NULL COMMENT 'Atmospheric pressure (hPa)',
            humidity INTEGER NOT NULL COMMENT 'Humidity (%)',
            uvi FLOAT NOT NULL COMMENT 'UV Index',
            weather_id INTEGER NOT NULL COMMENT 'Weather condition ID',
            wind_speed FLOAT NOT NULL COMMENT 'Wind speed (m/s)',
            wind_gust FLOAT NOT NULL DEFAULT 0 COMMENT 'Wind gust (m/s)',
            rain_1h FLOAT NOT NULL DEFAULT 0 COMMENT 'Rain volume (mm/h)',
            snow_1h FLOAT NOT NULL DEFAULT 0 COMMENT 'Snow volume (mm/h)',
            PRIMARY KEY (station_id, record_date, record_hour) COMMENT 'Ensures one record per hour per day'
        );
        """
        self.dh.create_table(sql=sql, table_name="weather.current_data")

    def create_weather_daily_forecast(self):
        sql = """
        CREATE TABLE weather.daily_forecast (
            station_id INTEGER NOT NULL COMMENT 'Station ID (Dublin)',
            position_lat FLOAT NOT NULL COMMENT 'Station latitude',
            position_lng FLOAT NOT NULL COMMENT 'Station longitude',
            record_time DATETIME NOT NULL COMMENT 'Data record time',
            record_date DATE NOT NULL COMMENT 'Data record date',
            forecast_date DATE NOT NULL COMMENT 'Predicted weather date',
            days_ahead INTEGER NOT NULL COMMENT 'Days ahead from base date',
            sunrise DATETIME NOT NULL COMMENT 'Sunrise time',
            sunset DATETIME NOT NULL COMMENT 'Sunset time',
            temp_day FLOAT NOT NULL COMMENT 'Avg temperature',
            temp_max FLOAT NOT NULL COMMENT 'Max temperature',
            temp_min FLOAT NOT NULL COMMENT 'Min temperature',
            feels_like_temp_day FLOAT NOT NULL COMMENT 'Avg feels like temperature',
            feels_like_temp_max FLOAT NOT NULL COMMENT 'Max feels like temperature',
            feels_like_temp_min FLOAT NOT NULL COMMENT 'Min feels like temperature',
            pressure INTEGER NOT NULL COMMENT 'Atmospheric pressure (hPa)',
            humidity INTEGER NOT NULL COMMENT 'Humidity (%)',
            uvi FLOAT NOT NULL COMMENT 'UV Index',
            weather_id INTEGER NOT NULL COMMENT 'Weather condition ID',
            wind_speed FLOAT NOT NULL COMMENT 'Wind speed (m/s)',
            wind_gust FLOAT NOT NULL DEFAULT 0 COMMENT 'Wind gust (m/s)',
            rain FLOAT NOT NULL DEFAULT 0 COMMENT 'Rain volume (mm)',
            snow FLOAT NOT NULL DEFAULT 0 COMMENT 'Snow volume (mm)',
            PRIMARY KEY (station_id, record_date, forecast_date)
        );
        """
        self.dh.create_table(sql=sql, table_name="weather.daily_forecast")

    def create_weather_hourly_forecast(self):
        sql = """
        CREATE TABLE weather.hourly_forecast (
            station_id INTEGER NOT NULL COMMENT 'Station ID (Dublin)',
            position_lat FLOAT NOT NULL COMMENT 'Station latitude',
            position_lng FLOAT NOT NULL COMMENT 'Station longitude',
            record_time DATETIME NOT NULL COMMENT 'Data record time',
            record_hourly_time DATETIME NOT NULL COMMENT 'Data record time rounded to hour',
            hours_ahead INTEGER NOT NULL COMMENT 'Hours ahead from base hour',
            forecast_hour DATETIME NOT NULL COMMENT 'Predicted hourly weather',
            temp FLOAT NOT NULL COMMENT 'Temperature (Celsius)',
            feels_like FLOAT NOT NULL COMMENT 'Feels like temperature (Celsius)',
            pressure INTEGER NOT NULL COMMENT 'Atmospheric pressure (hPa)',
            humidity INTEGER NOT NULL COMMENT 'Humidity (%)',
            uvi FLOAT NOT NULL COMMENT 'UV Index',
            weather_id INTEGER NOT NULL COMMENT 'Weather condition ID',
            wind_speed FLOAT NOT NULL COMMENT 'Wind speed (m/s)',
            wind_gust FLOAT NOT NULL DEFAULT 0 COMMENT 'Wind gust (m/s)',
            rain_1h FLOAT NOT NULL DEFAULT 0 COMMENT 'Rain volume (mm/h)',
            snow_1h FLOAT NOT NULL DEFAULT 0 COMMENT 'Snow volume (mm/h)',
            PRIMARY KEY (station_id, record_hourly_time, forecast_hour)
        );
        """
        self.dh.create_table(sql=sql, table_name="weather.hourly_forecast")

    def create_weather_weather_condition(self):
        # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
        sql = """
        CREATE TABLE weather.weather_condition (
            id DATETIME NOT NULL COMMENT 'Weather ID',
            name VARCHAR(50) NOT NULL COMMENT 'Weather name',
            description VARCHAR(200) NOT NULL COMMENT 'Weather description',
            icon VARCHAR(50) NOT NULL COMMENT 'Weather icon',
            PRIMARY KEY (id)
        );
        """
        self.dh.create_table(sql=sql, table_name="weather.weather_condition")

    def load_demo_availability_data(self):
        """Load demo availability data from CSV into the database."""
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "availability_demo.csv")
        df = pd.read_csv(file_path, sep=';')
        self.dh.save_df_data(df=df, db_name="bike", table_name="availability")

        
    def run(self):
        self.create_bike_database()
        self.create_bike_station()
        self.create_bike_availability()
        self.create_weather_schema()
        self.create_weather_current_date()
        self.create_weather_daily_forecast()
        self.create_weather_hourly_forecast()
        self.create_weather_weather_condition()
        self.load_demo_availability_data()
