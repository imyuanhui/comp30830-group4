import pickle
import datetime
import pandas as pd
import os

# Path to the model file
BIKE_MODEL_FILENAME = 'bike_availability_model.pkl'
BIKE_MODEL_PATH = os.path.join(os.getcwd(), "machine_learning", BIKE_MODEL_FILENAME)
STAND_MODEL_FILENAME = 'stand_availability_model.pkl'
STAND_MODEL_PATH = os.path.join(os.getcwd(), "machine_learning", STAND_MODEL_FILENAME)

# Global variable to store the model in memory
bike_model = None
stand_model = None

# Load models only once and keep it in memory
def load_model():
    global bike_model
    global stand_model
    if bike_model is None:
        with open(BIKE_MODEL_PATH, "rb") as f:
            bike_model = pickle.load(f)
        print("Bike Model loaded successfully.")
    if stand_model is None:
        with open(STAND_MODEL_PATH, "rb") as f:
            stand_model = pickle.load(f)
        print("Stand Model loaded successfully.")
    return bike_model, stand_model

# Feature extraction function
def extract_features(timestamp):
    """Extracts day_of_week, hour, and is_holiday from timestamp"""
    dt = datetime.datetime.fromtimestamp(int(timestamp))  # Convert to datetime
    day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
    hour = dt.hour  # Extract hour

    return day_of_week, hour

def predict_availability(station_id, timestamp, temp, target="bike"):
    # # Load the model once, if not already loaded
    # load_model()
    global bike_model
    global stand_model

    # Extract features
    day_of_week, hour = extract_features(timestamp)

    # Prepare input data for model
    input_data = pd.DataFrame([[station_id, temp, hour, day_of_week]],
                            columns=['station_id','max_air_temperature_celsius', 'hour', 'day_of_week'])

    # Make prediction
    if target == "bike":
        prediction = bike_model.predict(input_data)[0]
    elif target == "stand":
        prediction = stand_model.predict(input_data)[0]
    else:
        raise ValueError("Invalid target specified. Must be 'bike' or 'stand'.")
    return prediction



