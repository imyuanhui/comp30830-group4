// Declaring the global variables for map, markers, and UI states
let map; // Google Map instance
let markers = []; // Array to store station markers
let stationsVisible = true; // Toggle visibility of stations
let currentMode = "bike"; // Default mode: 'bike', can be toggled to 'stand'
let activeInfoWindow = null; // Track currently open InfoWindow
let bikeColor = "#5affa2"; // Color for bike availability markers
let bikeLabelColor = "black"; // Label color for bike markers
let standColor = "#FFD65A"; // Color for bike stand availability markers
let standLabelColor = "black"; // Label color for stand markers
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
  // Create a geolocation control button
  const locationButton = document.createElement("button");
  locationButton.textContent = "Current Location";
  locationButton.classList.add("custom-map-control-button");
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);

  locationButton.addEventListener("click", () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          // Center the map on the user's location
          map.setCenter(userLocation);

          // Add a marker for the user's location
          new google.maps.Marker({
            position: userLocation,
            map: map,
            icon: {
              path: google.maps.SymbolPath.CIRCLE,
              scale: 10,
              fillColor: "blue",
              fillOpacity: 0.8,
              strokeWeight: 2,
              strokeColor: "white",
            },
          });
        },
        () => {
          alert("Geolocation failed. Please enable location services.");
        }
      );
    } else {
      alert("Your browser doesn't support Geolocation.");
    }
  });
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

document.addEventListener("DOMContentLoaded", function () {
  const modeSwitch = document.getElementById("modeSwitch");
  modeSwitch.addEventListener("change", function () {
    currentMode = this.checked ? "stand" : "bike";
    updateMarkers();
  });
});

function setMarkerStyle(marker, mode = "default") {
  const station = marker.station_data;
  let fillColor;
  let label;
  let strokeColor;
  let strokeWeight;
  let labelColor;

  if (currentMode === "bike") {
    fillColor = bikeColor;
    labelColor = bikeLabelColor;
    label = station.details.available_bikes.toString();
  } else {
    fillColor = standColor;
    labelColor = standLabelColor;
    label = station.details.available_bike_stands.toString();
  }

  if (mode == "default") {
    strokeColor = "white";
    strokeWeight = 1;
  } else if (mode == "start_station") {
    strokeColor = "green";
    strokeWeight = 2;
  } else if (mode == "destination_station") {
    strokeColor = "red";
    strokeWeight = 2;
  }

  marker.setIcon({
    path: google.maps.SymbolPath.CIRCLE,
    scale: 15,
    fillColor: fillColor,
    fillOpacity: 0.9,
    strokeColor: strokeColor,
    strokeWeight: strokeWeight,
    labelOrigin: new google.maps.Point(0, 0),
  });

  marker.setLabel({
    text: label,
    fontSize: "14px",
    fontFamily: "sans-serif",
    color: labelColor,
  });
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

  alert(
    `Journey planned from ${startLocation.address} to ${destinationLocation.address} on ${day} at ${hour}.`
  );
  // mark start location on the map
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
      setMarkerStyle(marker, "start_station");
    } else if (stationId === destId) {
      setMarkerStyle(marker, "destination_station");
    }
  }
}

function goBackToForm() {
  document.getElementById("journey-form-panel").style.display = "block";
  document.getElementById("journey-result-panel").style.display = "none";
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
    <h1>🚲 Journey Plan Summary</h1>
    <p><strong>From:</strong> ${startLocation.address}</p>
    <p><strong>To:</strong> ${destinationLocation.address}</p>
    <p><strong>Day & Time:</strong> ${day}, ${hour}</p>

    <h2>📍 Start Station</h2>
    <p><strong>Name:</strong> ${data.start_station.name}</p>
    <p><strong>Available Bikes:</strong> ${data.start_station.details.available_bikes}</p>
    <p><strong>Last Updated:</strong> ${data.start_station.details.last_update}</p>

    <h2>🏁 Destination Station</h2>
    <p><strong>Name:</strong> ${data.destination_station.name}</p>
    <p><strong>Available Stands:</strong> ${data.destination_station.details.available_bike_stands}</p>
    <p><strong>Last Updated:</strong> ${data.destination_station.details.last_update}</p>
  `;
    highlightJourneyStations(
      data.start_station.id,
      data.destination_station.id
    );
  }
  document.getElementById("results-content").innerHTML = resultHtml;
}

let startLocation = null;
let destinationLocation = null;

function addJourneyLocationMarker(type, lat, lng) {
  const baseIcon = {
    labelOrigin: new google.maps.Point(20, 12),
    scaledSize: new google.maps.Size(40, 40),
  };
  let iconUrl = "";
  let labelText = "";

  if (type === "start") {
    iconUrl = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
    labelText = "S";
  } else if (type === "destination") {
    iconUrl = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
    labelText = "D";
  }

  new google.maps.Marker({
    position: { lat: lat, lng: lng },
    map: map,
    icon: { ...baseIcon, url: iconUrl },
    label: {
      text: labelText,
      color: "white",
      fontWeight: "bold",
    },
    title: type.charAt(0).toUpperCase() + type.slice(1),
  });
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
