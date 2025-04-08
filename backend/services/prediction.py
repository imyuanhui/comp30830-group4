import bz2
import pickle
import datetime
import pandas as pd
import os

# Path to the model file
MODEL_FILENAME = 'bike_availability_model_rf.pkl.bz2'
MODEL_PATH = os.path.join(os.getcwd(), "machine_learning", MODEL_FILENAME)

# Predefined holidays set
HOLIDAY_DATES = {
    "2025-01-01", "2025-02-03", "2025-03-17", "2025-04-21", "2025-05-05", 
    "2025-06-02", "2025-08-04", "2025-10-27", "2025-12-25", "2025-12-26"
}

# Global variable to store the model in memory
model = None

# Load the model only once and keep it in memory
def load_model():
    global model
    if model is None:
        with bz2.BZ2File(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    return model

# Feature extraction function
def extract_features(timestamp):
    """Extracts day_of_week, hour, and is_holiday from timestamp"""
    dt = datetime.datetime.fromtimestamp(int(timestamp))  # Convert to datetime
    day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
    hour = dt.hour  # Extract hour
        
    HOLIDAYS = {"2025-1-1", "2025-2-3", "2025-3-17", "2025-4-21", "2025-5-5", "2025-6-2", "2025-8-4", "2025-10-27", "2025-12-25", "2025-1-1", "2025-12-26"}
    is_holiday = 1 if dt.strftime("%Y-%m-%d") in HOLIDAYS else 0  # Check if holiday
    return day_of_week, hour, is_holiday

def predict_availability_status(station_id, timestamp):
    # Load the model once, if not already loaded
    load_model()

    # Extract features
    day_of_week, hour, is_holiday = extract_features(timestamp)

    # Prepare input data for model
    input_data = pd.DataFrame([[station_id, day_of_week, is_holiday, hour]],
                            columns=['station_id', 'day_of_week', 'is_holiday', 'hour'])

    # Make prediction
    prediction = model.predict(input_data)[0]
    return "sufficient" if prediction == 1 else "insufficient"



