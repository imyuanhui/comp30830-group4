import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        """
        Initializes and validates configurations for weather, bike API, and database.
        """
        load_dotenv()
        # Access individual values
        self.weather_config = WeatherConfig()
        self.weather_config.validate()
        self.bike_config = BikeConfig()
        self.bike_config.validate()
        self.db_config = DBConfig()
        self.db_config.validate()

    def get_weather_config(self):
        """
        Returns the loaded weather configuration object.

        Returns:
            WeatherConfig: The configuration object containing the weather API key.
        """
        return self.weather_config

    def get_bike_config(self):
        """
        Returns the loaded bike API configuration object.

        Returns:
            BikeConfig: The configuration object containing bike API key and station URI.
        """
        return self.bike_config

    def get_db_config(self):
        """
        Returns the loaded database configuration object.

        Returns:
            DBConfig: The configuration object containing DB credentials and URI.
        """
        return self.db_config


class WeatherConfig:
    def __init__(self):
        """Initialize weather configuration by loading the API key from environment variables."""
        self.weather_api_key = os.getenv("WEATHER_API_KEY")

    def validate(self):
        """
        Validates the presence of the weather API key.

        Raises:
            ValueError: If WEATHER_API_KEY is missing from the environment variables.
        """
        if not self.weather_api_key:
            raise ValueError("ERROR: No WEATHER_API_KEY found in .env.")


class BikeConfig:
    def __init__(self):
        """Initialize bike configuration by loading API details from environment variables."""
        self.bike_api_key = os.getenv("BIKE_API_KEY")
        self.bike_name = os.getenv("BIKE_NAME")
        self.stations_uri = os.getenv("BIKE_STATIONS_URL")

    def validate(self):
        """
        Validates the presence of required bike API configuration variables.

        Raises:
            ValueError: If any of the BIKE_API_KEY, BIKE_NAME, or BIKE_STATIONS_URL variables are missing.
        """
        missing_keys = []

        if not self.bike_api_key:
            missing_keys.append("BIKE_API_KEY")
        if not self.bike_name:
            missing_keys.append("BIKE_NAME")
        if not self.stations_uri:
            missing_keys.append("BIKE_STATIONS_URL")

        if missing_keys:
            raise ValueError(f"ERROR: Missing required environment variables: {', '.join(missing_keys)}")


class DBConfig:
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT")
        self.name = os.getenv("DB_NAME")
        self.uri = os.getenv("DB_URI")

    def validate(self):
        """
        Validates the presence of required database configuration variables.

        Raises:
            ValueError: If any of the DB_USER, DB_PASSWORD, DB_PORT, DB_NAME, or DB_URI variables are missing.
        """
        missing_keys = []
        if not self.user:
            missing_keys.append("DB_USER")
        if not self.password:
            missing_keys.append("DB_PASSWORD")
        if not self.port:
            missing_keys.append("DB_PORT")
        if not self.name:
            missing_keys.append("DB_NAME")
        if not self.uri:
            missing_keys.append("DB_URI")

        if missing_keys:
            raise ValueError(f"ERROR: Missing required environment variables: {', '.join(missing_keys)}")
