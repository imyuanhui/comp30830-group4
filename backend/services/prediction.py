import bz2
import pickle
import datetime
import numpy as np

def predict_availability_status(station_id, timestamp):
    with bz2.BZ2File("../machine_learning/bike_availability.pkl.bz2", "rb") as f:
        model = pickle.load(f)

    def extract_features(timestamp):
        """Extracts day_of_week, hour, and is_holiday from timestamp"""
        dt = datetime.datetime.fromtimestamp(int(timestamp))  # Convert to datetime
        day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
        hour = dt.hour  # Extract hour
        
        HOLIDAYS = {"2025-1-1", "2025-2-3", "2025-3-17", "2025-4-21", "2025-5-5", "2025-6-2", "2025-8-4", "2025-10-27", "2025-12-25", "2025-1-1", "2025-12-26"}
        is_holiday = 1 if dt.strftime("%Y-%m-%d") in HOLIDAYS else 0  # Check if holiday
        return day_of_week, hour, is_holiday
    
    day_of_week, hour, is_holiday = extract_features(timestamp)
    
    # Prepare input data for model
    input_data = np.array([[int(station_id), day_of_week, is_holiday, hour]])

    # Make prediction
    prediction = model.predict(input_data)[0]
    return prediction == 1 # sufficient:1, insufficient:0



