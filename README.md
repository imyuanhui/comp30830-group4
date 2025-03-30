# Dublin Bikes

This project provides a web-based interface to visualize real-time Dublin bike station data and weather conditions. The backend fetches, processes, and stores bike and weather data, while the frontend displays this information.

## Key Features

- Bike Station Information: Provides real-time data for bike availability and stand availability across all stations in Dublin.

- Station-Specific Insights: Displays weather conditions and historical data (bike availability and stand availability trends in the last 24-hour) for individual bike stations.

- Journey Planning: Helps users plan their rides by identifying suitable stations for starting and ending based on bike availability, stand availability, and proximity to the start and destination locations.

## Setup Guide

### 0. Setup Conda Virtual Environment

Before installing dependencies, create a Conda environment:

```bash
conda create --name dublin_bikes python=3.11
```

Activate the environment:

```bash
conda activate dublin_bikes
```

---

### 1. Install Requirements

Once the virtual environment is activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

---

### 2. Environment Variables Setup

#### 2.1 Rename `example.env`

Rename `example.env` to `.env`:

#### 2.2 Fill in Required Fields

Edit the `.env` file and provide the necessary API keys and database credentials:

```ini
# OpenWeather API key for fetching weather data
WEATHER_API_KEY=your_openweather_api_key

# MySQL database credentials
DB_USER=
DB_PASSWORD=
DB_PORT=
DB_URI=
DB_NAME=bike

# Google Maps API key (if required for frontend map rendering)
GOOGLE_MAPS_API_KEY=

# Dublin Bikes API credentials
BIKE_API_KEY=
BIKE_NAME=dublin
BIKE_STATIONS_URL=https://api.jcdecaux.com/vls/v1/stations
```

---

### 3. Local Database Setup

#### 3.1 Run Data Scraper

Navigate to the `backend/local_db_setup` folder and execute `main.py` to fetch and store bike and weather data:

```bash
python main.py
```

#### 3.2 Prevent Re-Setup

After the initial setup, **comment out** the following line in `main.py` to avoid resetting the database on every run:

```python
# db_set_up = DBSetUp()  # Comment this line out after the first run
```

---

### 4. Run the Server

Navigate to the `backend` folder and start the Flask server:

```bash
python app.py
```

---

### 5. Run the Client

Navigate to the `frontend` folder and open `index.html` in a browser:

Now, the web application should be running, displaying real-time Dublin bike station data and weather information. 🚲🌤️

Journey Planner: Helps users plan their bike rides by identifying stations with bikes and available slots, considering proximity.

Station Finder: Lets users find nearby stations based on various filters, such as distance or station name/address.

Station History: Provides historical bike availability data for specific stations to track trends and usage patterns.

Weather Integration: Retrieves current and historical weather data to help users decide the best time to travel or find a bike station based on weather conditions.
