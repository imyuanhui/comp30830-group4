```mermaid
sequenceDiagram
  actor User as User
  participant Browser as Web Browser (HTML + DOM)
  participant JS as Frontend Script (JS)
  participant Flask as Flask REST API
  participant Logic as Business Logic (Python)
  participant GoogleMaps as Google Maps API
  participant WeatherAPI as Weather API
  participant BikeAPI as Bike Station API
  
  

  User ->> Browser: Open Website
  Browser ->> JS: loadGoogleMapsAPI()
  JS ->> Flask: Request Google Maps API key
  Flask ->> Logic: get_google_maps_config()
  Logic -->> Flask: Return API key
  Flask -->> JS: Return API key
  JS ->> Browser: Inject script tag with API key
  Browser ->> GoogleMaps: Load Maps API
  GoogleMaps -->> Browser: Return SDK and execute initMap()

  Browser ->> JS: initMap()
  Note over JS: Create Google Map instance

  JS ->> Browser: Request geolocation
  Browser -->> JS: Return user response

  alt User grants permission
    JS ->> GoogleMaps: Center map on user location <br> Place marker
  else User denies
    JS ->> Browser: Show geolocation error
  end

  JS ->> Flask: Request weather data
  Note right of JS: For user location <br>(Dublin City Center as default)
  Flask ->> Logic: get_current_weather()
  Logic ->> WeatherAPI: Fetch weather data
  WeatherAPI -->> Logic: Return weather JSON
  Logic -->> Flask: Return weather JSON
  Flask -->> JS: Return weather JSON
  JS ->> Browser: Update top bar with weather

  JS ->> Flask: Request station list
  Flask ->> Logic: get_stations()
  Logic ->> BikeAPI: Fetch real-time Dublin Bike data
  BikeAPI -->> Logic: Return JSON
  Logic -->> Flask: Return station list
  Flask -->> JS: Return station data

  loop For each station
    JS ->> GoogleMaps: Create marker on map
    Note right of JS: Set marker styles <Br> Add click event listeners
  end

  JS ->> GoogleMaps: Init autocomplete inputs
  JS ->> Browser: Bind toggle listener
  JS ->> Browser: Populate 7-day dropdown
  JS ->> Browser: Bind timeMode toggle
  JS ->> Browser: Fill current date and time (disable input)
  JS ->> Browser: Render legend icons
  ```