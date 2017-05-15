var map;
var gcsMarker;
var drone_dict = {};
var lineList = [];


var lineSymbol = {
	path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
};

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
		icon: 'http://localhost:8000/map-icons/icon-gcs2-home.png'
	});
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

	if (id in drone_dict) {
		var marker = drone_dict[id];
		marker.setPosition({lat: lat, lng: lng});
	} 
	else {
		var marker = new google.maps.Marker({
			position: {lat: lat, lng: lng},
			icon: 'http://localhost:8000/map-icons/icon-gcs2-blue.png',
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


function draw_line(startLat, startLng, endLat, endLng) {
	var line = new google.maps.Polyline({
		path: [{lat: startLat, lng: startLng}, {lat: endLat, lng: endLng}],
		icons: [{
			icon: lineSymbol,
			offset: '100%'
		}],
		// geodesic: true,
		// strokeColor: '#FF0000',
		// strokeOpacity: 1.0,
		// strokeWeight: 2,
		map: map
	});
	// console.log(startLat);

	// var lineCoordinate = [{lat: startLat, lng: startLng}, {lat: endLat, lng: endLng}];
 //  var line = new google.maps.Polyline({
 //    path: lineCoordinate,
 //    geodesic: true,
 //    strokeColor: '#FF0000',
 //    strokeOpacity: 1.0,
 //    strokeWeight: 2
 //  });

 //  line.setMap(map);



	lineList.push(line);
}

function remove_all_lines() {
	for (var i=0; i<lineList.length; i++) {
		lineList[i].setMap(null);
	}

	lineList = [];
}


function mark_gcs_position(lat, lng) {
	gcsMarker.setPosition({lat: lat, lng: lng});
	gcsMarker.setMap(map);
}

function distance(lat1, lng1, lat2, lng2) {
	return google.maps.geometry.spherical.computeDistanceBetween(
		{lat: lat1, lng: lng1}, {lat: lat2, lng: lng2});
}
