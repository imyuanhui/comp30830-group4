import pickle
import datetime
import pandas as pd
import os

# === File Paths for Models and Encoded Mappings ===
MODEL_DIR = os.path.join(os.getcwd(), "machine_learning")
BIKE_MODEL_PATH = os.path.join(MODEL_DIR, 'bike_availability_model.pkl')
STAND_MODEL_PATH = os.path.join(MODEL_DIR, 'stand_availability_model.pkl')
BIKE_ENCODED_PATH = os.path.join(MODEL_DIR, 'station_bike_encoding.pkl')
STAND_ENCODED_PATH = os.path.join(MODEL_DIR, 'station_stand_encoding.pkl')

# === Global Variables for In-Memory Caching ===
bike_model = None
stand_model = None
mean_bike_encoded = None
mean_stand_encoded = None

def load_model():
    """
    Load prediction models and station_id encodings into memory if not already loaded.
    """
    global bike_model, stand_model, mean_bike_encoded, mean_stand_encoded

    if bike_model is None:
        with open(BIKE_MODEL_PATH, "rb") as f:
            bike_model = pickle.load(f)
        print("Bike model loaded.")

    if stand_model is None:
        with open(STAND_MODEL_PATH, "rb") as f:
            stand_model = pickle.load(f)
        print("Stand model loaded.")

    if mean_bike_encoded is None:
        with open(BIKE_ENCODED_PATH, "rb") as f:
            mean_bike_encoded = pickle.load(f)
        print("Bike station encoding loaded.")

    if mean_stand_encoded is None:
        with open(STAND_ENCODED_PATH, "rb") as f:
            mean_stand_encoded = pickle.load(f)
        print("Stand station encoding loaded.")

    return bike_model, stand_model

def extract_features(timestamp):
    """
    Extracts day_of_week and hour from the input Unix timestamp.
    
    Parameters:
        timestamp (int): Unix timestamp.
    
    Returns:
        tuple: (day_of_week, hour)
    """
    dt = datetime.datetime.fromtimestamp(int(timestamp))
    return dt.weekday(), dt.hour

def predict_availability(station_id, timestamp, temp, target="bike"):
    """
    Predicts bike or stand availability for a given station, timestamp, and temperature.
    
    Parameters:
        station_id (int): ID of the bike station.
        timestamp (int): Unix timestamp.
        temp (float): Max air temperature in Celsius.
        target (str): "bike" or "stand".
    
    Returns:
        float: Predicted availability.
    """
    global bike_model, stand_model, mean_bike_encoded, mean_stand_encoded

    # Extract time-based features
    day_of_week, hour = extract_features(timestamp)

    if target == "bike":
        # Encode station_id based on historical bike availability
        station_id_encoded = mean_bike_encoded.get(station_id, mean_bike_encoded.mean())

        input_data = pd.DataFrame(
            [[station_id_encoded, temp, hour, day_of_week]],
            columns=['station_id_encoded1', 'max_air_temperature_celsius', 'hour', 'day_of_week']
        )

        prediction = bike_model.predict(input_data)[0]

    elif target == "stand":
        # Encode station_id based on historical stand availability
        station_id_encoded = mean_stand_encoded.get(station_id, mean_stand_encoded.mean())

        input_data = pd.DataFrame(
            [[station_id_encoded, temp, hour, day_of_week]],
            columns=['station_id_encoded2', 'max_air_temperature_celsius', 'hour', 'day_of_week']
        )

        prediction = stand_model.predict(input_data)[0]

    else:
        raise ValueError("Invalid target specified. Use 'bike' or 'stand'.")

    return prediction