import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# JCDecaux API Configuration
API_KEY = "your_api_key"  # Please Replace with your actual API key
CONTRACT_NAME = "dublin"
URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",  # Please Replace with your MySQL username
    "password": "your_password",  # Please Replace with your MySQL password
    "database": "dublin_bikes"
}

def fetch_bike_data():
    """Fetch Dublin bike station data from JCDecaux API"""
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def store_data_in_mysql(data):
    """Store bike station data in MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            cursor = conn.cursor()

            insert_query = """
            write the query here.
            """

            for station in data:
                values = (
                    station["number"],
                    station["name"],
                    station["address"],
                    station["position"]["lat"],
                    station["position"]["lng"],
                    station["bike_stands"],
                    station["available_bike_stands"],
                    station["available_bikes"],
                    station["status"],
                    station["last_update"] // 1000  # It is Converting milliseconds to seconds
                )
                cursor.execute(insert_query, values)

            conn.commit()
            print(f"{cursor.rowcount} records inserted/updated successfully.")

    except Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    bike_data = fetch_bike_data()
    if bike_data:
        store_data_in_mysql(bike_data)
