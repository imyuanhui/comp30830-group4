import bz2
import pickle
import datetime
import pandas as pd
import os

def predict_availability_status(station_id, timestamp):
    model_filename = 'bike_availability_model_rf.pkl.bz2'
    model_path = os.path.join(os.getcwd(), "machine_learning", model_filename)
    print(model_path)
    with bz2.BZ2File(model_path, "rb") as f:
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
    # Prepare input data as a DataFrame with the correct column names
    input_data = pd.DataFrame([[station_id, day_of_week, is_holiday, hour]],
                            columns=['station_id', 'day_of_week', 'is_holiday', 'hour'])

    # Make prediction
    prediction = model.predict(input_data)[0]
    return "sufficient" if prediction == 1 else "insufficient"



