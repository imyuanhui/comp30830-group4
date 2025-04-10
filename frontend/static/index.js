// ================= Global State & Config =================
let map; // Google Maps instance
let markers = []; // All bike station markers
let journeyMarkers = []; // Markers for start/destination of planned journey

let startLocation = null;
let destinationLocation = null;
let showUserLocation = false; // Whether the user's current location is shown on the map
let showJourneyMarkers = false; // Whether the planned journey markers are currently displayed
let activeInfoWindow = null; // The currently open InfoWindow (used to close others when a new one opens)
let currentMode = "bike"; // "bike" or "stand" - determines which availability type is shown

const bikeMarkerColor = "#71BF8D"; // Marker color for bike availability
const standMarkerColor = "#F7CE68"; // Marker color for stand availability

const daySelect = document.getElementById("day-select"); // <select> dropdown for travel day
const hourSelect = document.getElementById("hour-select"); // <select> dropdown for travel hour

// ================= Initialization =================
// Load the Google Maps API dynamically and initialize the map
function loadGoogleMapsAPI() {
  fetch(`/api/config`)
    .then((response) => response.json())
    .then((config) => {
      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=${config.GOOGLE_MAPS_API_KEY}&libraries=places&callback=initMap`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    })
    .catch((error) =>
      console.error("Failed to load Google Maps API Key:", error)
    );
}

// Initialize map, center on Dublin, and set up autocomplete inputs
function initMap() {
  console.log("Map initialized");
  const dublin = { lat: 53.3498, lng: -6.2603 }; // Default map center

  // Create a new Google Map instance
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });
  getMyLocation(map);
  getStations();

  // Initialize autocomplete for journey planning inputs
  initAutocomplete("start-location");
  initAutocomplete("destination");
  addMyLocationButton(map);
}

function addMyLocationButton(map) {
  const controlDiv = document.createElement("div");

  const button = document.createElement("button");
  button.innerHTML = "📍 My Location";
  button.classList.add("custom-map-control-button");

  button.addEventListener("click", () => {
    getMyLocation(map);
  });

  controlDiv.appendChild(button);
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(controlDiv);
}

// Get the user's current location and center the map on it
function getMyLocation(map) {
  if (!navigator.geolocation) {
    alert("Your browser doesn't support Geolocation.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      const userLocation = {
        lat: latitude,
        lng: longitude,
      };

      showWeatherInfo("Your Location: ", latitude, longitude);
      map.setCenter(userLocation);
      map.setZoom(14);
      showUserLocation = true;
      updateLegend();
      const userMarker = new google.maps.Marker({
        position: userLocation,
        map: map,
        title: "You are here",
        icon: {
          url: "./static/assets/current_location.png",
          scaledSize: new google.maps.Size(40, 40),
        },
        animation: google.maps.Animation.DROP,
      });
    },
    (error) => {
      alert("Geolocation failed. Please enable location services.");
      // Use Dublin center as default weather
      showWeatherInfo("Dublin City Center", 53.3498, -6.2603);
    }
  );
}

// ================= Station Markers =================
// Fetch station list from backend and create markers on map
function getStations() {
  fetch(`/api/stations`)
    .then((response) => response.json())
    .then((data) => {
      if (!data || !data.data || !Array.isArray(data.data)) {
        throw new Error(
          "Invalid data format: Expected an object with a 'data' array"
        );
      }
      addMarkers(data.data);
    })
    .catch((error) => {
      console.error("Error fetching stations data:", error);
    });
}

// Create a marker and InfoWindow for each station
function addMarkers(stations) {
  for (const station of stations) {
    const marker = createStationMarker(station);
    setMarkerStyle(marker);

    const defaultContent = `
      <div>
        <h3>${station.name}</h3>
        <p><strong>Available Bikes:</strong> ${
          station.details.available_bikes || 0
        }</p>
        <p><strong>Available Bike Stands:</strong> ${
          station.details.available_bike_stands || 0
        }</p>
        <p><strong>Last Update Time:</strong> ${
          station.details.last_update || "N/A"
        }</p>
        <div id="chart_bike_${
          station.id
        }" style="width: 300px; height: 200px;"></div>
        <div id="chart_stands_${
          station.id
        }" style="width: 300px; height: 200px;"></div>
      </div>
    `;

    const infoWindow = new google.maps.InfoWindow({ content: defaultContent });

    attachStationClickListener(marker, station, infoWindow, defaultContent);
    markers.push(marker);
  }
}

// Creates and returns a Google Maps marker for a bike station
function createStationMarker(station) {
  return new google.maps.Marker({
    position: {
      lat: parseFloat(station.lat),
      lng: parseFloat(station.lon),
    },
    map: map,
    title: station.name,
    station_number: station.id,
    station_data: station,
  });
}

// Adds click listener to marker that opens an InfoWindow with live weather and station details
function attachStationClickListener(
  marker,
  station,
  infoWindow,
  defaultContent
) {
  marker.addListener("click", () => {
    marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);

    if (activeInfoWindow) activeInfoWindow.close();

    fetchWeatherData(station.lat, station.lon)
      .then(({ iconUrl, temp, weatherDescription }) => {
        const content = `
          <div>
            <img src="${iconUrl}" alt="Weather icon" class="weather-icon" />
            <h3>${station.name}</h3>
            <p><strong>Weather:</strong> ${temp}℃ (${weatherDescription})</p>
            <p><strong>Available Bikes:</strong> ${
              station.details.available_bikes || 0
            }</p>
            <p><strong>Available Bike Stands:</strong> ${
              station.details.available_bike_stands || 0
            }</p>
            <p><strong>Last Update Time:</strong> ${
              station.details.last_update || "N/A"
            }</p>
            <div id="chart_bike_${
              station.id
            }" style="width: 300px; height: 200px;"></div>
            <div id="chart_stand_${
              station.id
            }" style="width: 300px; height: 200px;"></div>
          </div>
        `;
        infoWindow.setContent(content);
        infoWindow.open(map, marker);
        google.maps.event.addListenerOnce(infoWindow, "domready", () => {
          drawStationChart(station);
        });
        activeInfoWindow = infoWindow;
      })
      .catch(() => {
        infoWindow.setContent(defaultContent);
        infoWindow.open(map, marker);
        activeInfoWindow = infoWindow;
      });
  });
}

// Draw historical availability charts (24hr) for bikes and stands
function drawStationChart(station) {
  fetch(`/api/stations/history/demo/${station.id}`)
    .then((response) => response.json())
    .then((station_past) => {
      console.log(station_past);
      // Define container for the chart
      if (typeof google !== "undefined" && google.charts) {
        google.charts.load("current", { packages: ["corechart"] });
        google.charts.setOnLoadCallback(() => {
          const bikeChartData = new google.visualization.DataTable();
          const standChartData = new google.visualization.DataTable();

          bikeChartData.addColumn("string", "Hour");
          bikeChartData.addColumn("number", "Available Bikes");

          standChartData.addColumn("string", "Hour");
          standChartData.addColumn("number", "Available Bike Stands");

          // Loop through the data
          for (const row of station_past.data) {
            bikeChartData.addRow([
              row.record_hour,
              Number(row.available_bikes),
            ]);
            standChartData.addRow([
              row.record_hour,
              Number(row.available_bike_stands),
            ]);
          }
          console.log(bikeChartData);

          const baseChartOptions = {
            legend: { position: "bottom" },
            width: 400,
            height: 200,
            chartArea: {
              left: 50,
              top: 30,
            },
          };

          const bikeOptions = {
            ...baseChartOptions,
            title: "🚲 24-Hour Bike Availability",
            colors: [bikeMarkerColor],
          };

          const standOptions = {
            ...baseChartOptions,
            title: "📍 24-Hour Stand Availability",
            colors: [standMarkerColor],
          };

          const bikeChart = new google.visualization.ColumnChart(
            document.getElementById(`chart_bike_${station.id}`)
          );
          bikeChart.draw(bikeChartData, bikeOptions);

          const standChart = new google.visualization.ColumnChart(
            document.getElementById(`chart_stand_${station.id}`)
          );
          standChart.draw(standChartData, standOptions);
        });
      } else {
        console.error("Google Charts is not loaded.");
      }
      google.charts.load("current", { packages: ["corechart"] });
    })
    .catch((error) => {
      console.error("Error fetching past 24 hours availability info:", error);
    });
}

// ================= UI Controls: Mode & Legend =================
// Set up toggle switch to switch between "bike" and "stand" modes
function setupModeToggle() {
  const modeToggle = document.getElementById("modeToggle");

  // Listen for toggle change and update current mode accordingly
  modeToggle.addEventListener("change", function () {
    currentMode = this.checked ? "stand" : "bike";
    updateMarkers(); // Refresh the map markers based on selected mode
    updateLegend(); // Refresh the legends
  });
}

// Re-style all markers based on the current mode
function updateMarkers() {
  for (const marker of markers) {
    setMarkerStyle(marker);
  }
}

// ================= UI Controls: Date & Time =================
// Enable or disable time inputs depending on "now" vs "future" selection
function setupTimeToggle() {
  document.querySelectorAll('input[name="timeMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      const isFuture = document.getElementById("mode-future").checked;

      daySelect.disabled = !isFuture;
      hourSelect.disabled = !isFuture;

      if (!isFuture) {
        // reset form to current time
        setNowAsDefaultTime();
      } else {
        updateHourOptions(daySelect.value);
      }
    });
  });
}

// Populate the day dropdown with the next 7 days
function setupDaySelector() {
  const now = new Date();
  for (let i = 0; i < 5; i++) {
    const date = new Date(now);
    date.setDate(now.getDate() + i);
    // format: 2024-04-01 (Tue)
    const yyyyMMdd = date.toISOString().split("T")[0];
    const weekday = date.toLocaleDateString("en-IE", { weekday: "short" });
    const label = `${yyyyMMdd} (${weekday})`;
    const option = new Option(label, yyyyMMdd);
    if (i === 0) option.selected = true;

    daySelect.appendChild(option);
  }

  daySelect.addEventListener("change", () => {
    updateHourOptions(daySelect.value);
  });
}

// Populate the hour dropdown based on selected day and current time
function updateHourOptions(selectedDateStr) {
  const now = new Date();
  const isToday = selectedDateStr === now.toISOString().split("T")[0];
  const currentHour = now.getHours();

  hourSelect.innerHTML = "";

  for (let h = 0; h < 24; h++) {
    if (isToday && h <= currentHour) continue;
    const timeStr = `${String(h).padStart(2, "0")}:00`;
    hourSelect.appendChild(new Option(timeStr, timeStr));
  }

  // Optionally select first available
  if (hourSelect.options.length > 0) {
    hourSelect.options[0].selected = true;
  }
}

// Set the time selector to the current time and disable input
function setNowAsDefaultTime() {
  const now = new Date();
  const todayStr = now.toISOString().split("T")[0];
  const hour = String(now.getHours()).padStart(2, "0");
  const minute = String(now.getMinutes()).padStart(2, "0");
  const nowStr = `${hour}:${minute}`;

  daySelect.value = todayStr;

  // Set hour select with one current-time option
  hourSelect.innerHTML = `<option value="${nowStr}" selected>${nowStr} (Now)</option>`;
  hourSelect.disabled = true;
}

// ================= Journey Planning =================
// Set up Google Places Autocomplete for input fields
function initAutocomplete(field) {
  const input = document.getElementById(field);
  const autocomplete = new google.maps.places.Autocomplete(input);

  autocomplete.addListener("place_changed", function () {
    const place = autocomplete.getPlace();
    if (!place.geometry) {
      alert("No details available for the selected location.");
      return;
    }

    const lat = place.geometry.location.lat();
    const lon = place.geometry.location.lng();
    console.log(`Selected ${field}:`, place.formatted_address, lat, lon);

    // Store lat/lng for journey planning
    if (field === "start-location") {
      startLocation = { lat, lon, address: place.formatted_address };
    } else if (field === "destination") {
      destinationLocation = { lat, lon, address: place.formatted_address };
    }
  });
}

// Send API request to plan a journey (with or without timestamp)
function planJourney() {
  const day = daySelect.value;
  const hour = hourSelect.value;
  const isNow = document.getElementById("mode-now").checked;

  if (!startLocation || !destinationLocation) {
    alert("Please select valid start and destination locations.");
    return;
  }

  // center the map on start Location and mark start and destination locations on the map
  map.setCenter({ lat: startLocation.lat, lng: startLocation.lon });
  addJourneyLocationMarker("start", startLocation.lat, startLocation.lon);
  addJourneyLocationMarker(
    "destination",
    destinationLocation.lat,
    destinationLocation.lon
  );

  // build journey API URL
  let url = `/api/plan-journey?start_lat=${startLocation.lat}&start_lon=${startLocation.lon}&dest_lat=${destinationLocation.lat}&dest_lon=${destinationLocation.lon}`;
  // If mode is ‘right now’, omit timestamp from API
  if (!isNow) {
    const unixTimestamp = toUnixTimestamp(day, hour);
    url += `&timestamp=${unixTimestamp}`;
  }
  console.log(`API Call: ${url}`);

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log("Journey Plan Response:", data);
      showJourneyResultPanel(
        day,
        hour,
        startLocation,
        destinationLocation,
        data
      );
    })
    .catch((error) => {
      console.error("Error sending journey data:", error);
    });
}

// Highlight the markers for start and destination stations
function highlightJourneyStations(startId, destId) {
  for (const marker of markers) {
    const stationId = marker.station_data.id;

    if (stationId === startId) {
      setMarkerStyle(marker, "selected");
    } else if (stationId === destId) {
      setMarkerStyle(marker, "selected");
    }
  }
}

// Add a marker to the map for start or destination location
function addJourneyLocationMarker(type, lat, lng) {
  const iconUrl = `./static/assets/${type}_location.png`;

  const marker = new google.maps.Marker({
    position: { lat, lng },
    map: map,
    icon: {
      url: iconUrl,
      scaledSize: new google.maps.Size(40, 40),
    },
  });
  journeyMarkers.push(marker);
}

// Display journey plan result in the result panel
function showJourneyResultPanel(
  day,
  hour,
  startLocation,
  destinationLocation,
  data
) {
  let resultHtml;

  document.getElementById("journey-form-panel").style.display = "none";
  document.getElementById("journey-result-panel").style.display = "block";
  if (data.error) {
    resultHtml = `
      <p>🚫 No recommended bike stations found. Please try again.</p>
    `;
    document.getElementById("results-content").innerHTML = resultHtml;
    return;
  }

  const isFuture = document.getElementById("mode-future").checked;
  let predictionWarning = "";
  let predictionLabel = "";
  let startStationBikes = data.start_station.details.available_bikes;
  let destStationStands = data.start_station.details.available_bike_stands;
  let startStationIconUrl = `http://openweathermap.org/img/w/${data.start_station.prediction.icon}.png`;
  let destLocationIconUrl = `http://openweathermap.org/img/w/${data.destination_station.prediction.icon}.png`;

  if (isFuture) {
    predictionWarning = `
      <div class="prediction-warning">
        Start and destination station availability is estimated from historical trends. Actual conditions may vary.
      </div>
    `;
    predictionLabel = "Predicted ";
    startStationBikes =
      data.start_station.prediction.predicted_bike_availability;
    destStationStands =
      data.destination_station.prediction.predicted_stand_availability;
  }

  resultHtml = `
    ${predictionWarning}
    <h4 class="section-title">🚲 Journey Plan Summary</h4>
    <div class="info-card">
      <p><strong>From:</strong><br> ${startLocation.address}</p>
      <p><strong>To:</strong><br> ${destinationLocation.address}</p>
      <p><strong>Day & Time:</strong><br> ${day}, ${hour}</p>
    </div>

    <h4 class="section-title">📍 Start Station</h4>
    <div class="station-info-box">
      <div class="station-text">
        <p><strong>Name:</strong><br> ${data.start_station.name}</p>
        <p><strong>Weather:</strong><br> ${data.start_station.prediction.temp}℃ (${data.start_station.prediction.description})</p>
        <p><strong>${predictionLabel}Available Bikes:<br></strong> ${startStationBikes}</p>
      </div>
      <div class="station-icon">
        <img src="${startStationIconUrl}" alt="Weather icon" class="weather-icon" />
      </div>
    </div>

    <h4 class="section-title">🏁 Destination Station</h4>
    <div class="station-info-box">
      <div class="station-text">
        <p><strong>Name:</strong><br>${data.destination_station.name}</p>
        <p><strong>Weather:</strong><br> ${data.destination_station.prediction.temp}℃ (${data.destination_station.prediction.description})</p>
        <p><strong>${predictionLabel}Available Stands:</strong><br> ${destStationStands}</p>
      </div>
      <div class="station-icon">
        <img src="${destLocationIconUrl}" alt="Weather icon" class="weather-icon" />
      </div>
    </div>
    
    <div class="legend"></div>
  `;

  showJourneyMarkers = true;
  document.getElementById("results-content").innerHTML = resultHtml;
  highlightJourneyStations(data.start_station.id, data.destination_station.id);
  updateLegend();
}

// Clear all journey markers from the map
function clearJourneyLocationMarkers() {
  for (const marker of journeyMarkers) {
    marker.setMap(null); // Remove from map
  }
  journeyMarkers = []; // Clear the array
  showJourneyMarkers = false; // Optional: hide legend icons
}

// Return to the input form view and reset journey display
function goBackToForm() {
  document.getElementById("journey-form-panel").style.display = "block";
  document.getElementById("journey-result-panel").style.display = "none";
  clearJourneyLocationMarkers();
  updateMarkers();
  updateLegend();
}

// ================= Utilities =================
// Fetch weather for a certain time and location
function fetchWeatherData(lat, lon) {
  return fetch(`/api/weather/current?lat=${lat}&lon=${lon}`)
    .then((response) => response.json())
    .then((data) => {
      if (!data || !data.weather || !data.weather[0]) {
        throw new Error("Invalid weather data format");
      }
      const iconUrl = `http://openweathermap.org/img/w/${data.weather[0].icon}.png`;
      const temp = data.temp;
      const weatherDescription = data.weather[0].description;
      return { iconUrl, temp, weatherDescription };
    });
}

// Display live weather info in the top bar
function showWeatherInfo(locationName, lat, lon) {
  const weatherInfo = document.getElementById("weather-info");
  fetchWeatherData(lat, lon)
    .then(({ iconUrl, temp, weatherDescription }) => {
      weatherInfo.innerHTML = `${locationName}:
        <img src="${iconUrl}" alt="Weather Icon" style="width: 25px; vertical-align: middle; margin-left: 10px;"> 
        <span style="font-weight: bold; color: #aee0ed; margin-left: 5px;">${temp}°C (${weatherDescription})</span>`;
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
      weatherInfo.innerHTML =
        "<span style='color: red;'>Failed to load weather</span>";
    });
}

// Set the icon and animation for a marker based on availability
function setMarkerStyle(marker, mode = "default") {
  const station = marker.station_data;
  let availability;
  let color;
  let iconMode = currentMode;

  if (currentMode === "bike") {
    availability = station.details.available_bikes;
  } else {
    availability = station.details.available_bike_stands;
  }

  if (availability == 0) {
    color = "gray";
  } else if (availability <= 5) {
    color = "yellow";
  } else {
    color = "green";
  }

  const iconUrl = `./static/assets/${iconMode}_${color}.png`;

  if (mode == "selected") {
    marker.setIcon({
      url: iconUrl,
      scaledSize: new google.maps.Size(60, 60),
    });

    marker.setAnimation(google.maps.Animation.BOUNCE);
  } else {
    marker.setIcon({
      url: iconUrl,
      scaledSize: new google.maps.Size(40, 40),
    });
    marker.setAnimation(null);
  }
}

// Convert date and hour to a Unix timestamp (in seconds)
function toUnixTimestamp(day, hour) {
  const dateTimeString = `${day}T${hour}:00`; // add seconds for full ISO string
  const date = new Date(dateTimeString); // parse as local time
  return Math.floor(date.getTime() / 1000); // convert ms to seconds
}

// Update the legend panel based on current UI state
function updateLegend() {
  const legends = document.getElementsByClassName("legend"); // 回傳的是多個元素

  const content = `
    <h4>Legend</h4>
    <ul>
      <li><img src="./static/assets/${currentMode}_green.png" /> Available (6+)</li>
      <li><img src="./static/assets/${currentMode}_yellow.png" /> Low (1–5)</li>
      <li><img src="./static/assets/${currentMode}_gray.png" /> Empty (0)</li>

      ${
        showUserLocation
          ? `<li><img src="./static/assets/current_location.png" /> Your Location</li>`
          : ""
      }

      ${
        showJourneyMarkers
          ? `
        <li><img src="./static/assets/start_location.png" /> Start location</li>
        <li><img src="./static/assets/destination_location.png" /> Destination</li>
        `
          : ""
      }
    </ul>
  `;

  for (const legend of legends) {
    legend.innerHTML = content;
  }
}

// ================= App Entry & Bootstrapping =================
// Set up app components after DOM content is loaded
document.addEventListener("DOMContentLoaded", () => {
  loadGoogleMapsAPI();
  setupModeToggle();
  setupDaySelector();
  setupTimeToggle();
  setNowAsDefaultTime();
  updateLegend();
});
