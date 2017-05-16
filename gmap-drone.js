var map;
var gcsMarker;
var drone_dict = {};
var lineList = [];

// var icons_url = {
// 	'home': 'http://localhost:8000/map-icons/icon-gcs2-home.png',
// 	'idle': 'http://localhost:8000/map-icons/icon-gcs2-blue.png',
// 	'tracking' : 'http://localhost:8000/map-icons/icon-gcs2-green.png',
// 	'red': 'http://localhost:8000/map-icons/icon-gcs2-red.png',
// 	'yellow': 'http://localhost:8000/map-icons/icon-gcs2-blue.png'
// }

var icons_url = {
	'home': 'map-icons/icon-gcs2-home.png',
	'idle': 'map-icons/icon-gcs2-blue.png',
	'tracking' : 'map-icons/icon-gcs2-green.png',
	'red': 'map-icons/icon-gcs2-red.png',
	'yellow': 'map-icons/icon-gcs2-blue.png'
}

// Initialize the map. Called when this file is loaded.
function initMap() {
	var GCSLatLng = {lat: 36.374092, lng: 127.365638};

	map = new google.maps.Map(document.getElementById('map'), {
		center: GCSLatLng,
		zoom: 17,
		mapTypeId: google.maps.MapTypeId.SATELLITE,
		disableDefaultUI: true
	});

	map.addListener('click', map_clicked);

	//Locations of the GCS
	gcsMarker = new google.maps.Marker({
		position: GCSLatLng,
		map: map,
		icon: icons_url['home']
	});

	console.log("hello");
}

// map listener
function map_clicked(e) {
	var latLng = e.latLng;
	var lat = latLng.lat();
	var lng = latLng.lng();

	//console.log("map_click_event " + lat + " " + lng);
	jsCommunicator.emit_signal("map_click_event " + lat + " " + lng);
}


// updates the position of the marker
// creates a new marker if the id is not recognized
function update_marker(id, lat, lng) {
	console.log("update marker!");
	if (id in drone_dict) {
		var marker = drone_dict[id];
		marker.setPosition({lat: lat, lng: lng});
	} 
	else {
		var marker = new google.maps.Marker({
			position: {lat: lat, lng: lng},
			icon: icons_url['idle'],
			label: {
			    text: id + '',
			    color: 'white',
			    fontSize: '10px'
			},
			map: map
		});

		marker.addListener('click', function() {
			markerPos = marker.getPosition()
			gcsPos = gcsMarker.getPosition()

			if (gcsMarker.getMap() != null) {
				dist = google.maps.geometry.spherical
					.computeDistanceBetween(markerPos, gcsPos);
			}
			else {
				dist = "no_gcs_position";
			}

			// console.log("marker_click_event " + id + " " + dist);
			jsCommunicator.emit_signal("marker_click_event " + id + " " + dist);
		});

		drone_dict[id] = marker;
	}
}

function change_drone_status(id, status){

	if (id in drone_dict){
		var marker = drone_dict[id];
		marker.setIcon(icons_url[status]);
	}
	
}

// removes marker from the map
function remove_marker(id) {
	if (id in drone_dict) {
		drone_dict[id].setMap(null);
		drone_dict[id] = null;
		// do not delete the ID so that it can be recycled
		// also deleting will hurt performance
	}
}

// removes all markers from the map
function remove_all_markers() {
	for (var id in drone_dict) {
		drone_dict[id].setMap(null);
	}
	drone_dict = {};
}

