var latitud;
var longitud;
var map;
var marker;
var geocoder;
$(document).ready(function() {


    $.ajax({
            contentType: "application/json; charset=utf-8",
            type: "POST",
            url: "getIP",
            dataType: "json"
        })
        .done(function(data) {
            if (data.error) {
                console.log("ERROR")
                console.log(data.error);
            } else {
                latitud = data['latitude'];
                longitud = data['longitude'];

                mapboxgl.accessToken = 'pk.eyJ1IjoiZ3JlZ29yeTIxMTIiLCJhIjoiY2p1cHRlaGl4MHNlcDRlbWtnczJ3Ym8wayJ9.zeXo71zkVPhy2fctm_K71g';
                map = new mapboxgl.Map({
                    container: 'map',
                    center: [longitud, latitud],
                    zoom: 7,
                    style: 'mapbox://styles/mapbox/streets-v11'
                });

                geocoder = new MapboxGeocoder({
                    accessToken: mapboxgl.accessToken,
                    mapboxgl: mapboxgl
                });
                geocoder.on('result', function(results) {
                    if (typeof marker !== 'undefined') {
                        marker.remove();
                    }
                    document.getElementById('lon').value = JSON.stringify(results.result.geometry.coordinates[0]);
                    document.getElementById('lat').value = JSON.stringify(results.result.geometry.coordinates[1]);
                })

                map.on('click', function(e) {
                    if (typeof marker !== 'undefined') {
                        marker.remove();
                        geocoder.mapMarker.remove();
                    }
                    document.getElementById('lon').value = JSON.stringify(e.lngLat.wrap().lng);
                    document.getElementById('lat').value = JSON.stringify(e.lngLat.wrap().lat);

                    marker = new mapboxgl.Marker()
                        .setLngLat(e.lngLat.wrap())
                        .addTo(map); // add the marker to the map
                });

                map.addControl(geocoder);
            }
        });



});