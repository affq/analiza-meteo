const defaultZoom = 7;
const defaultLat = 51.9189046;
const defaultLng = 19.1343786;

var m = L.map('map').setView([defaultLat, defaultLng], defaultZoom);

// var socket = io();

let wojLayer;
axios.get('dane_przestrzenne/woj.geojson')
.then(function(response) {
        wojLayer = L.geoJson(response.data, {
            style: function(feature) {
                return {
                    color: 'black',
                    fillOpacity: 0.1
                };
            }
        }).addTo(m);
    }
);

let powLayer;
axios.get('dane_przestrzenne/pow.geojson')
.then(function(response) {
        powLayer = L.geoJson(response.data, {
            style: function(feature) {
                return {
                    color: 'black',
                    fillOpacity: 0.1
                };
            }
        }).addTo(m);
    }
);

m.on('zoomend', function() {
    if (m.getZoom() < 8) {
        m.removeLayer(powLayer);
        m.addLayer(wojLayer);
    } else {
        m.removeLayer(wojLayer);
        m.addLayer(powLayer);
    }
});
