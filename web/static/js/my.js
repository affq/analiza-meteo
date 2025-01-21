const defaultZoom = 6;
const defaultLat = 51.9189046;
const defaultLng = 19.1343786;

var m = L.map('map').setView([defaultLat, defaultLng], defaultZoom);

var socket = io('http://127.0.0.1:5000');

let wybranaJednostka = {};

function setWybranaJednostka(feature, layer, type) {
    if (wybranaJednostka.layer) {
        if (wybranaJednostka.type === 'woj') {
            wybranaJednostka.layer.setStyle({'fillOpacity': 0});
        }
        else if (wybranaJednostka.type === 'pow') {
            wybranaJednostka.layer.setStyle({'fillOpacity': 0});
        }
    }
    wybranaJednostka.feature = feature;
    wybranaJednostka.layer = layer;
    wybranaJednostka.type = type;

    if (type === 'woj') {
        layer.setStyle({'fillOpacity': 0.5});
    }
    else if (type === 'pow') {
        layer.setStyle({'fillOpacity': 0.5});
    }
}

let wojLayer;
fetch('/geojson/woj.geojson')
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(function(data) {
        wojLayer = L.geoJson(data, {
            style: function(feature) {
                return {
                    color: 'black',
                    fillOpacity: 0,
                    weight: 3
                };
            },
            onEachFeature: function(feature, layer) {
                layer.bindTooltip(feature.properties.name, {
                    direction: 'center',
                    offset: L.point(0, 0)
                });
                layer.on('click', function(e) {
                    setWybranaJednostka(feature, layer, 'woj');
                });
            }
        }).addTo(m);
    })
    .catch(function(error) {
        console.error('Error fetching the GeoJSON data:', error);
    });


let powLayer;
fetch('/geojson/pow.geojson')
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(function(data) {
        powLayer = L.geoJson(data, {
            style: function(feature) {
                return {
                    color: 'black',
                    fillOpacity: 0,
                    weight: 1
                };
            },
            onEachFeature: function(feature, layer) {
                layer.bindTooltip(feature.properties.name, {
                    direction: 'center',
                    offset: L.point(0, 0)
                });
                layer.on('click', function(e) {
                    setWybranaJednostka(feature, layer, 'pow');
                });
            }
        });
    })
    .catch(function(error) {
        console.error('Error fetching the GeoJSON data:', error);
    });


m.on('zoomend', function() {
    if (m.getZoom() < 8) {
        m.removeLayer(powLayer);
        m.addLayer(wojLayer);
    } else {
        m.addLayer(wojLayer);
        m.addLayer(powLayer);
    }
});

function wybierzJednostke() {
    if (wybranaJednostka) {
        console.log(wybranaJednostka);
        socket.emit('wybrano', {"name": wybranaJednostka.feature.properties.name, "type": wybranaJednostka.type});
    }
    else {
        socket.emit('wybrano', {});
    }
}

var legend = L.control({position: 'bottomright'});
legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'legend');
    div.innerHTML += '<button style="font-size: 25px; padding=10px" onclick=wybierzJednostke()>Zatwierdź wybór</button>';
    return div
};
legend.addTo(m);
