// Declaring the global variables for map, markers, and UI states
let map; // Google Map instance
let showUserLocation = false;
let showJourneyMarkers = false;
let journeyMarkers = [];
let markers = []; // Array to store station markers
let stationsVisible = true; // Toggle visibility of stations
let currentMode = "bike"; // Default mode: 'bike', can be toggled to 'stand'
let activeInfoWindow = null; // Track currently open InfoWindow
let bikeColor = "#71BF8D"; // Color for bike availability markers
let bikeLabelColor = "black"; // Label color for bike markers
let standColor = "#F7CE68"; // Color for bike stand availability markers
let standLabelColor = "black"; // Label color for stand markers
const daySelect = document.getElementById("day-select"); // Get the day selection dropdown element
const hourSelect = document.getElementById("hour-select"); // Get the hour selection dropdown element
let now = new Date(); // Get the current date and time at the moment the page loads
let currentHour = now.getHours(); // Extract the current hour (0 to 23) to determine which time slots have already passed today
const BASE_URL = "http://127.0.0.1:8000";

// Fetch API key from backend and dynamically load Google Maps API script
fetch(`${BASE_URL}/api/config`)
  .then((response) => response.json())
  .then((config) => {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${config.GOOGLE_MAPS_API_KEY}&libraries=places&callback=initMap`;
    script.async = true;
    document.head.appendChild(script);
  })
  .catch((error) => console.error("Failed to load API Key:", error));

// Initialize Google Maps and set up event listeners
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
}

// Get and display user's current location
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
    }
  );
}

// Fetch station data and add markers to the map
function getStations() {
  //todo: The availability info should retrieve directly from API response, only the data for chart is from database
  fetch(`${BASE_URL}/api/stations`)
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

// Create and configure markers for each station
function addMarkers(stations) {
  console.log(stations);
  // Create a marker for each station
  for (const station of stations) {
    const marker = new google.maps.Marker({
      position: {
        lat: parseFloat(station.lat),
        lng: parseFloat(station.lon),
      },
      map: map,
      title: station.name,
      station_number: station.id,
      station_data: station,
    });

    setMarkerStyle(marker);

    // Create an InfoWindow with station details
    const defaultContent = `
            <div>
                <h3>${station.name}</h3>
                <p><strong>Available Bikes:</strong> ${
                  station.details.available_bikes || "N/A"
                }</p>
                <p><strong>Available Bike Stands:</strong> ${
                  station.details.available_bike_stands || "N/A"
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

    const infoWindow = new google.maps.InfoWindow({
      content: defaultContent,
    });

    // Add click listener to show station details and weather info
    marker.addListener("click", () => {
      marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);

      // Close the currently open InfoWindow, if any
      if (activeInfoWindow) {
        activeInfoWindow.close();
      }

      // Fetch real-time weather data for the station's location
      fetch(
        `${BASE_URL}/api/weather/current?lat=${parseFloat(
          station.lat
        )}&lon=${parseFloat(station.lon)}`
      )
        .then((response) => response.json())
        .then((weather) => {
          console.log(weather);
          const icon_url =
            "http://openweathermap.org/img/w/" +
            weather.weather[0].icon +
            ".png";
          const temp = weather.temp;
          const desp = weather.weather[0]["description"];
          const content = `
                        <div>
                            <div class="modal-weather">
                                <img src="${icon_url}" alt="Weather icon" />
                                <span>${desp} ${temp}℃</span>
                            </div>
                            <h3>${station.name}</h3>
                            <p><strong>Available Bikes:</strong> ${
                              station.details.available_bikes || "N/A"
                            }</p>
                            <p><strong>Available Bike Stands:</strong> ${
                              station.details.available_bike_stands || "N/A"
                            }</p>
                            <p><strong>Last Update Time:</strong> ${
                              station.details.last_update || "N/A"
                            }</p>
                            <div id="chart_bike_${station.id}"></div>
                            <div id="chart_stand_${station.id}"></div>
                        </div>
                    `;
          infoWindow.setContent(content);
          infoWindow.open(map, marker);

          google.maps.event.addListenerOnce(infoWindow, "domready", () => {
            drawStationChart(station);
          });

          // Set this InfoWindow as the active one
          activeInfoWindow = infoWindow;
        })
        .catch((error) => {
          console.error("Error fetching weather info:", error);
          // Show default infoWindow content if fetch fails
          infoWindow.setContent(defaultContent);
          infoWindow.open(map, marker);
          activeInfoWindow = infoWindow;
        });
    });

    markers.push(marker);
  }
}

function drawStationChart(station) {
  fetch(`${BASE_URL}/api/stations/history/demo/${station.id}`)
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
            colors: [bikeColor],
          };

          const standOptions = {
            ...baseChartOptions,
            title: "📍 24-Hour Stand Availability",
            colors: [standColor],
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

function toggleMode() {
  currentMode = currentMode === "bike" ? "stand" : "bike";
  const button = document.getElementById("modeToggle");
  button.textContent = currentMode === "bike" ? "Bike" : "Stand";
  updateMarkers();
}

// Sets up the toggle behavior between "bike" and "stand" mode
function setupModeToggle() {
  const modeSwitch = document.getElementById("modeSwitch");

  // Listen for toggle change and update current mode accordingly
  modeSwitch.addEventListener("change", function () {
    currentMode = this.checked ? "stand" : "bike";
    updateMarkers(); // Refresh the map markers based on selected mode
    updateLegend(); // Refresh the legends
  });
}

function setupTimeToggle() {
  document.querySelectorAll('input[name="timeMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      const isFuture = document.getElementById("mode-future").checked;

      daySelect.disabled = !isFuture;
      hourSelect.disabled = !isFuture;

      if (!isFuture) {
        setNowAsDefaultTime();
      } else {
        updateHourOptions(daySelect.value);
      }
    });
  });
}

function setupDaySelector() {
  const now = new Date();
  for (let i = 0; i < 7; i++) {
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

// Setup when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  setupModeToggle();
  setupDaySelector();
  setupTimeToggle();
  setNowAsDefaultTime();
  updateLegend();
});

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

function updateMarkers() {
  for (const marker of markers) {
    setMarkerStyle(marker);
  }
}

function planJourney() {
  const day = document.getElementById("day-select").value;
  const hour = document.getElementById("hour-select").value;

  if (!startLocation || !destinationLocation) {
    alert("Please select valid start and destination locations.");
    return;
  }

  map.setCenter({lat: startLocation.lat, lng: startLocation.lon});
  addJourneyLocationMarker("start", startLocation.lat, startLocation.lon);
  // mark destination location on the map
  addJourneyLocationMarker(
    "destination",
    destinationLocation.lat,
    destinationLocation.lon
  );

  fetch(
    `${BASE_URL}/api/plan-journey?start_lat=${startLocation.lat}&start_lon=${startLocation.lon}&dest_lat=${destinationLocation.lat}&dest_lon=${destinationLocation.lon}`
  )
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

function goBackToForm() {
  document.getElementById("journey-form-panel").style.display = "block";
  document.getElementById("journey-result-panel").style.display = "none";
  clearJourneyLocationMarkers();
  updateMarkers();
  updateLegend();
}

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
  } else {
    resultHtml = `
    <h3>🚲 Journey Plan Summary</h3>
    <p><strong>From:</strong><br> ${startLocation.address}</p>
    <p><strong>To:</strong><br> ${destinationLocation.address}</p>
    <p><strong>Day & Time:</strong><br> ${day}, ${hour}</p>

    <h4>📍 Start Station</h4>
    <p><strong>Name:</strong> ${data.start_station.name}</p>
    <p><strong>Available Bikes:</strong> ${data.start_station.details.available_bikes}</p>
    <p><strong>Last Updated:</strong> ${data.start_station.details.last_update}</p>

    <h4>🏁 Destination Station</h4>
    <p><strong>Name:</strong> ${data.destination_station.name}</p>
    <p><strong>Available Stands:</strong> ${data.destination_station.details.available_bike_stands}</p>
    <p><strong>Last Updated:</strong> ${data.destination_station.details.last_update}</p>

    <div class="legend"></div>
  `;
  }
  showJourneyMarkers = true;
  document.getElementById("results-content").innerHTML = resultHtml;
  highlightJourneyStations(data.start_station.id, data.destination_station.id);
  updateLegend();
}

let startLocation = null;
let destinationLocation = null;

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

function clearJourneyLocationMarkers() {
  for (const marker of journeyMarkers) {
    marker.setMap(null);        // Remove from map
  }
  journeyMarkers = [];          // Clear the array
  showJourneyMarkers = false;   // Optional: hide legend icons
}

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

function showWeatherPrompt(lat, lon) {
  fetch(`${BASE_URL}/api/weather/current?lat=${lat}&lon=${lon}`)
    .then((response) => response.json())
    .then((data) => {
      if (!data) {
        throw new Error(
          "Invalid data format: Expected an object with a 'data' array"
        );
      }
      var iconurl =
        "http://openweathermap.org/img/w/" + data.weather[0].icon + ".png";
      showModal(
        "<p><strong>Current weather:</strong> " +
          data.weather[0].description +
          "<img src= " +
          iconurl +
          "> </img></p>"
      );
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
    });
}

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

window.onload = function () {
  if (typeof google !== "undefined") {
    initMap();
  }
};

// Function to display the modal
function showModal(content) {
  const modal = document.getElementById("myModal");
  const modalText = document.getElementById("modalText");
  // Set the content with HTML (HTML is parsed here)
  modalText.innerHTML = content;
  // Display the modal
  modal.style.display = "block";
  // Close the modal when the user clicks on the <span> element
  const closeBtn = document.getElementsByClassName("close")[0];
  closeBtn.onclick = function () {
    modal.style.display = "none";
  };

  // Close the modal if the user clicks anywhere outside of the modal
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}
