L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
     maxZoom: 26,
  maxNativeZoom: 19
    
}).addTo(map);

L.control.scale({imperial: false}).addTo(map);
