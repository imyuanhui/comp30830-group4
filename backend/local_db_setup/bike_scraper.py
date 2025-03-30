import requests
import datetime
import os
from config import Config
from db_helper import DBHelper
import pandas as pd


class BikeScraper:
    """
    This class fetches real-time bike station data from an external API, 
    stores it in a local file for logging, and saves relevant station 
    and availability data into a database.
    """
    
    def __init__(self):
        # Load bike API configuration details
        bike_config = Config().get_bike_config()

        # Fetch bike station data from the API
        self.r = requests.get(bike_config.stations_uri, params={"apiKey": bike_config.bike_api_key, "contract": bike_config.bike_name})
        
        # Initialize database helper
        self.dh = DBHelper()

        # Store the current timestamp
        self.now = datetime.datetime.now()

    def write_to_file(self):
        """Writes the API response data to a file for record-keeping."""
        
        # Check if 'bike_data' directory exists, if not, create it
        if not os.path.exists('bike_data'):
            os.mkdir('bike_data')
            print("Folder 'bike_data' created!")
        else:
            print("Folder 'bike_data' already exists.")
        
        # Format the current timestamp for filename consistency
        formatted_now = self.now.strftime("%Y-%m-%d_%H-%M-%S")

        # Save the API response to a new file
        with open(f"bike_data/bikes_{formatted_now}", "w") as file:
            file.write(self.r.text)

    def write_to_db(self):
        """Processes and writes bike station and availability data into the database."""
        
        # Load API response JSON into a pandas DataFrame
        df = pd.read_json(self.r.text)

        # Extract latitude and longitude from the 'position' column
        df[['position_lat', 'position_lng']] = pd.json_normalize(df['position'])
        
        # Convert timestamp fields to datetime format
        df['last_update'] = pd.to_datetime(df['last_update'], unit='ms')
        df['record_time'] = self.now

        # Define relevant columns for the 'station' table
        station_cols = ['id', 'name', 'address', 'position_lat', 'position_lng']
        
        # Rename 'number' column to 'id' for consistency
        station_df = df.rename(columns={'number': 'id'})
        station_df = station_df[station_cols]
        
        # Fetch existing station data from the database
        existing_station_df = self.dh.query_data(sql="SELECT * FROM bike.station")
        
        # Identify new stations not already in the database
        new_station_df = station_df[~station_df['id'].isin(existing_station_df['id'])]

        # Insert new stations into the database if there are any
        if len(new_station_df) > 0:
            self.dh.save_df_data(df=new_station_df, db_name="bike", table_name="station")
        else:
            print("No new data need to be saved for bike.station")
        
        # Define relevant columns for the 'availability' table
        availability_cols = ['station_id', 'status', 'available_bikes', 'available_bike_stands', 'last_update', 'record_time']
        
        # Rename 'number' column to 'station_id' for consistency
        availability_df = df.rename(columns={'number': 'station_id'})
        availability_df = availability_df[availability_cols]

        # Insert availability data into the database
        self.dh.save_df_data(df=availability_df, db_name="bike", table_name="availability")

    def run(self):
        """Executes the full scraping process: saving data to file and database."""
        self.write_to_file()
        self.write_to_db()
