# Dublin Bikes

This project provides a web-based interface to visualize real-time Dublin bike station data and weather conditions. The backend fetches, processes, and stores bike and weather data, while the frontend displays this information.

## Key Features

- Bike Station Information: Displays real-time data on bike and stand availability for all bike stations across Dublin.

- Station-Specific Insights: Shows current weather conditions and visualizes historical trends in bike and stand availability over the past 24 hours for each station.

- Real-time Journey Planning: Assists users in planning their trips by suggesting optimal start and end stations based on live bike/stand availability and proximity to the user's specified locations.

- Future Journey Planning: Enables users to plan rides up to 5 days in advance using a predictive model. Provides forecasts of bike and stand availability along with expected weather conditions for recommended stations.

## Setup Guide

### 0. Create Conda Virtual Environment

First, create and activate a Conda environment for the project:

```bash
conda create --name dublin_bikes python=3.11
conda activate dublin_bikes
```

---

### 1. Install Dependencies

Once the environment is activated, install all required Python packages:

```bash
pip install -r requirements.txt
```

---

### 2. Configure Environment Variables

#### 2.1 Rename the Environment File

Rename the example environment file:

```bash
mv example.env .env
```

#### 2.2 Add API Keys and Credentials

Edit the `.env` file and fill in the following fields:

```ini
# OpenWeather API key
WEATHER_API_KEY=your_openweather_api_key

# MySQL database credentials
DB_USER=
DB_PASSWORD=
DB_PORT=
DB_URI=
DB_NAME=bike

# Google Maps API key (optional, for map rendering in frontend)
GOOGLE_MAPS_API_KEY=

# Dublin Bikes API credentials
BIKE_API_KEY=
BIKE_NAME=dublin
BIKE_STATIONS_URL=https://api.jcdecaux.com/vls/v1/stations

# Base Url cofiguration
BASE_URL=http://your-server-ip:8000
```

---

### 3. Initialize Local Database

Navigate to the `backend/local_db_setup` directory and run the following script to fetch and store initial bike and weather data:

```bash
python main.py
```

> **Note:** This step is only required during the initial setup.

---

### 4. Run the Server

Navigate to the `backend` folder and start the Flask server:

```bash
python app.py
```

---

### 5. Launch the Web Application

Open your browser and enter the correct server IP and port.

The web app should now be running, showing real-time Dublin bike station data and weather insights.

---
