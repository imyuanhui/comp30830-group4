let map;
let markers = [];
let stationsVisible = true;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 53.3498, lng: -6.2603 },
        zoom: 14,
    });

    addStationMarker("Pearse Street", 53.3437935, -6.2479865, 13, 17);
}

function addStationMarker(name, lat, lng, bikes, spaces) {
    const marker = new google.maps.Marker({
        position: { lat, lng },
        map,
        title: `${name}\nAvailable Bikes: ${bikes}\nAvailable Parking Spaces: ${spaces}`,
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `<strong>${name}</strong><br>Available Bikes: ${bikes}<br>Available Parking Spaces: ${spaces}`,
    });

    marker.addListener("click", () => {
        infoWindow.open(map, marker);
    });

    markers.push(marker);
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
