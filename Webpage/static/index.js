let map;
let markers = [];
let stationsVisible = true;

fetch("http://127.0.0.1:5000/api/config")
    .then(response => response.json())
    .then(config => {
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${config.GOOGLE_MAPS_API_KEY}&callback=initMap`;
        script.async = true;
        document.head.appendChild(script);
    })
    .catch(error => console.error("Failed to load API Key:", error));

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

function getMyLocation(map){
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
                        lng: position.coords.longitude
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
                            strokeColor: "white"
                        }
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


function getStations(){
    //todo: The availability info should retrieve directly from API response, only the data for chart is from database 
    fetch("http://127.0.0.1:5000/api/stations")
    .then((response) => response.json())
    .then((data) => {
        if (!data || !data.data || !Array.isArray(data.data)) {
            throw new Error("Invalid data format: Expected an object with a 'data' array");
        }
        addMarkers(data.data);
    })
    .catch((error) => {
        console.error("Error fetching stations data:", error);
    })
}

function addMarkers(stations){
    console.log(stations);
    // Create a marker for each station
    for (const station of stations){
        const marker = new google.maps.Marker({
            position: {
                lat: parseFloat(station.lat),
                lng: parseFloat(station.lon),
            },
            map: map,
            title: station.name,
            station_number: station.id,
        });

        const infoWindow = new google.maps.InfoWindow({
            content:`
            <div>
            <h3>${station.name}</h3>
            <p><strong>Address:</strong> ${station.address || "N/A"}</p>
            <p><strong>Available Bikes:</strong> ${station.details.available_bikes || "N/A"}</p>
            <p><strong>Available Bike Stands:</strong> ${station.details.available_bike_stands || "N/A"}</p>
            <p><strong>Last Update Time:</strong> ${station.details.last_update || "N/A"}</p>
            </div>
            `,
        });

        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });

        markers.push(marker);
    }
}

function planJourney() {
    const start = document.getElementById("start-location").value;
    const dest = document.getElementById("destination").value;
    const day = document.getElementById("day-select").value;
    const hour = document.getElementById("hour-select").value;

    alert(`Journey planned from ${start} to ${dest} on ${day} at ${hour}.`);
}

function showWeatherPrompt() {
    alert("You clicked on the weather information!");
}

window.onload = function () {
    if (typeof google !== "undefined") {
        initMap();
    }
};
