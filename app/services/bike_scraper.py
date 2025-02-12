import requests
import datetime
import os
from config import Config
from db_helper import DBHelper
import pandas as pd


class BikeScraper:
    def __init__(self):
        bike_config = Config().get_bike_config()
        self.r = requests.get(bike_config.stations_uri, params={"apiKey": bike_config.bike_api_key, "contract": bike_config.bike_name})
        self.dh = DBHelper()
        self.now = datetime.datetime.now()

    def write_to_file(self):
        if not os.path.exists('bike_data'):
            os.mkdir('bike_data')
            print("Folder 'bike_data' created!")
        else:
            print("Folder 'bike_data' already exists.")

        formatted_now = str(self.now).replace(" ", "_")
        with open(f"bike_data/bikes_{formatted_now}", "w") as file:
            file.write(self.r.text)

    def write_to_db(self):
        df = pd.read_json(self.r.text)
        df[['position_lat', 'position_lng']] = pd.json_normalize(df['position'])
        df['last_update'] = pd.to_datetime(df['last_update'], unit='ms')
        df['record_time'] = self.now
        print(df)
        station_cols = ['id', 'name', 'address', 'position_lat', 'position_lng']
        station_df = df.rename(columns={'number': 'id'})
        station_df = station_df[station_cols]
        existing_station_df = self.dh.query_data(sql="SELECT * FROM bike.station")
        new_station_df = station_df[~station_df['id'].isin(existing_station_df['id'])]

        if len(new_station_df) > 0:
            self.dh.save_df_data(df=new_station_df, db_name="bike", table_name="station")
        else:
            print("No new data need to be saved for bike.station")

        availability_cols = ['station_id', 'status', 'available_bikes', 'available_bike_stands', 'last_update', 'record_time']
        availability_df = df.rename(columns={'number': 'station_id'})
        availability_df = availability_df[availability_cols]

        self.dh.save_df_data(df=availability_df, db_name="bike", table_name="availability")

    def run(self):
        self.write_to_file()
        self.write_to_db()
