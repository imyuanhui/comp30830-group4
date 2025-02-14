import json


class Config:
    def __init__(self):
        # Load the JSON file
        with open('config.json', 'r') as file:
            config = json.load(file)
        # Access individual values
        self.weather_config = WeatherConfig(config["WeatherAPI"])
        self.bike_config = BikeConfig(config["BikeAPI"])
        self.db_config = DBConfig(config["Database"])

    def get_weather_config(self):
        return self.weather_config

    def get_bike_config(self):
        return self.bike_config

    def get_db_config(self):
        return self.db_config


class WeatherConfig:
    def __init__(self, weather_conn):
        self.weather_api_key = weather_conn["weather_api_key"]


class BikeConfig:
    def __init__(self, bike_conn):
        self.bike_api_key = bike_conn["bike_api_key"]
        self.bike_name = bike_conn["bike_name"]
        self.stations_uri = bike_conn["stations_uri"]


class DBConfig:
    def __init__(self, db_conn):
        self.user = db_conn["user"]
        self.password = db_conn["password"]
        self.port = db_conn["port"]
        self.name = db_conn["name"]
        self.uri = db_conn["uri"]
