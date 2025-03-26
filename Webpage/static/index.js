let map;
let markers = [];
let stationsVisible = true;
let currentMode = "bike"; // <- declare this at the top
let activeInfoWindow = null;

fetch("http://127.0.0.1:5000/api/config")
  .then((response) => response.json())
  .then((config) => {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${config.GOOGLE_MAPS_API_KEY}&callback=initMap`;
    script.async = true;
    document.head.appendChild(script);
  })
  .catch((error) => console.error("Failed to load API Key:", error));

// Initialize Google Maps
function initMap() {
  console.log("Map initialized");
  const dublin = { lat: 53.3498, lng: -6.2603 };
  // The map, centered at Dublin
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: dublin,
  });
  getMyLocation(map);
  getStations();
}

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

function getStations() {
  //todo: The availability info should retrieve directly from API response, only the data for chart is from database
  fetch("http://127.0.0.1:5000/api/stations")
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

    const defaultContent = `
            <div>
                <h3>${station.name}</h3>
                <p><strong>Address:</strong> ${station.address || "N/A"}</p>
                <p><strong>Available Bikes:</strong> ${
                  station.details.available_bikes || "N/A"
                }</p>
                <p><strong>Available Bike Stands:</strong> ${
                  station.details.available_bike_stands || "N/A"
                }</p>
                <p><strong>Last Update Time:</strong> ${
                  station.details.last_update || "N/A"
                }</p>
            </div>
        `;

    const infoWindow = new google.maps.InfoWindow({
      content: defaultContent,
    });

    marker.addListener("click", () => {
      // Close the currently open InfoWindow, if any
      if (activeInfoWindow) {
        activeInfoWindow.close();
      }

      // Fetch data when the marker is clicked
      fetch(
        "http://127.0.0.1:5000/api/weather/current?lat=" +
          parseFloat(station.lat) +
          "&lon=" +
          parseFloat(station.lon)
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
                            <p><strong>Address:</strong> ${
                              station.address || "N/A"
                            }</p>
                            <p><strong>Available Bikes:</strong> ${
                              station.details.available_bikes || "N/A"
                            }</p>
                            <p><strong>Available Bike Stands:</strong> ${
                              station.details.available_bike_stands || "N/A"
                            }</p>
                            <p><strong>Last Update Time:</strong> ${
                              station.details.last_update || "N/A"
                            }</p>
                        </div>
                    `;
          infoWindow.setContent(content);
          infoWindow.open(map, marker);

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

function toggleMode() {
  currentMode = currentMode === "bike" ? "slot" : "bike";
  const button = document.getElementById("modeToggle");
  button.textContent = currentMode === "bike" ? "Bike" : "Slot";
  updateMarkers();
}

document.addEventListener("DOMContentLoaded", function () {
  const modeSwitch = document.getElementById("modeSwitch");
  modeSwitch.addEventListener("change", function () {
    currentMode = this.checked ? "slot" : "bike";
    updateMarkers();
  });
});

function setMarkerStyle(marker) {
  const station = marker.station_data;
  let fillOpacity = 0.5;
  let fillColor = "gray";
  let label = "0";

  if (currentMode === "bike") {
    fillColor = "lightgreen";
    fillOpacity = 0.9;
    label = station.details.available_bikes.toString();
  } else {
    fillColor = "gray";
    fillOpacity = 0.7;
    label = station.details.available_bike_stands.toString();
  }

  marker.setIcon({
    path: google.maps.SymbolPath.CIRCLE,
    scale: 15,
    fillColor: fillColor,
    fillOpacity: fillOpacity,
    strokeWeight: 1,
    strokeColor: "white",
    labelOrigin: new google.maps.Point(0, 0),
  });

  marker.setLabel({
    text: label,
    fontSize: "14px",
    fontFamily: "sans-serif",
    color: "black",
  });
}

function updateMarkers() {
  for (const marker of markers) {
    setMarkerStyle(marker);
  }
}

function planJourney() {
  const start = document.getElementById("start-location").value;
  const dest = document.getElementById("destination").value;
  const day = document.getElementById("day-select").value;
  const hour = document.getElementById("hour-select").value;

  alert(`Journey planned from ${start} to ${dest} on ${day} at ${hour}.`);
}

function showWeatherPrompt(lat, lon) {
  fetch("http://127.0.0.1:5000/api/weather/current?lat=" + lat + "&lon=" + lon)
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
