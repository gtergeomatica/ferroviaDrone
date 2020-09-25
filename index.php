<?php  
 ?> 
<!doctype html> 
<html> <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Ferrovia Drone</title>
    <!--link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.3/dist/leaflet.css" /-->
	 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
   integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
   crossorigin=""/>
   <link rel="stylesheet" href="./leaflet-search/src/leaflet-search.css" />
  
   
   
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.0.6/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.0.6/dist/MarkerCluster.Default.css" />
	
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" 
integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.6.3/css/all.css" 
integrity="sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/" crossorigin="anonymous">
    <link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.15.4/dist/bootstrap-table.min.css">
	 
<style>
 #map
{
    width: 100px;
    height:100px;
    min-height: 400px;
    min-width: 100%;
    display: block;
    top: 5%;
    
}
html, body {
    height: 100%;
}
#map-holder{
    height: 100%;
}
.fill {
    min-height: 100%;
    height: 100%;
    width: 100%;
    max-width: 100%;
}
.container{
    max-width:60em;
    padding: 0.2em;
}
</style> </head> <body> <div class="container"> <div class="row"> <div class="col-sm-12"> <h1> 
<img src="./img/drone.png" alt="Logo" width="5%"--> 
Tool per il calcolo online del tragitto (pagina demo in via di sviluppo)</h1> </div> </div>
<div class="row">
	<div class="col-md-12">
		<div id="map"></div>
	</div>
</div>
<hr>
<form name="form1" action="index.php" method="GET">
<div class="row">
	<div class="col-md-12">
		<label for="nome"> Seleziona quale punto catturare</label><br>
		<label class="radio-inline"><input type="radio" name="georef" id="input1">Punto di partenza</label><br>
		<label class="radio-inline"><input type="radio" name="georef" id="input2">Punto di arrivo</label>
	</div><div class="col-md-6">
	<h3>Punto di partenza</h3>
	<div class="form-group">
	<label for="lat1"> Latitudine </label> <font color="red">*</font>
	<input type="text" name="lat1" id="lat1" class="form-control" required="">
	</div>

	<div class="form-group">
	<label for="lon1"> Longitudine </label> <font color="red">*</font>
	<input type="text" name="lon1" id="lon1" class="form-control" required="">
	</div>

	</div>
	<div class="col-md-6">
		<h3>Punto di arrivo</h3>
		<div class="form-group">
		<label for="lat2"> Latitudine </label> <font color="red">*</font>
		<input type="text" name="lat2" id="lat2" class="form-control" required="">
		</div>

		<div class="form-group">
		<label for="lon2"> Longitudine </label> <font color="red">*</font>
		<input type="text" name="lon2" id="lon2" class="form-control" required="">
		</div>
	</div>
	
	<div class="col-md-12">
		<h3><label for="cars">Scegli il formato di esportazione:</label></h3>
		<select name="cars" id="cars" form="carform">
		  <option value="csv">CSV</option>
		  <option value="kml">KML</option>
		  <option value="gml">GML</option>
		  <option value="geojson">GeoJSON</option>
		  <option value="shape">ESRI Shapefile</option>
		</select>
    </div>	
	

</div> 
<hr>
<div class="row">
<button  type="submit" class="btn btn-primary">Calcola percorso 3D</button>
</div> 
</form> 
  
  
  
  <div class="row">
		


<!-- Footer -->
<footer class="page-footer font-small blue pt-4">
  <!-- Footer Links -->
  <div class="container-fluid text-center text-md-left"> <hr>
  <!-- Copyright -->
  <div class="footer-copyright text-center py-3">2020, <a href="https://www-gter.it"> Gter srl</a> Copyleft. Codice sorgente disponibile su 
  <a target="_new" href="https://github.com/gtergeomatica/ferroviaDrone"> <i class="fab fa-github"></i> GitHub </a>
  <br> Lavoro sviluppato nell'ambito del progetto FerroviaDrone cofinanziato dal progetto 
  <a target="_new" href="https://www.start4-0.it/"> <img src="./img/logo_finanziatore.png" alt="Start 4.0" width="5%"></a>
    
  </div>
    <!-- Grid row -->
    <div class="row">
    </div>
    <!-- Grid row -->
  </div> </footer> <!-- Footer -->
    <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" 
crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" 
integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js" 
integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/bootstrap-table@1.15.4/dist/bootstrap-table.min.js"></script>
  <!--script src="./bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.js"></script--> 
<!--script src="https://unpkg.com/leaflet@1.0.3/dist/leaflet-src.js"></script--> 
 <!-- Make sure you put this AFTER Leaflet's CSS -->
 <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
   integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
   crossorigin=""></script>
   
   
   <script src="./leaflet-search/src/leaflet-search.js"></script>


<script src="https://unpkg.com/leaflet.markercluster@1.0.6/dist/leaflet.markercluster-src.js"></script> 
<script src="https://unpkg.com/leaflet.featuregroup.subgroup"></script> 
<!--script src="./leaflet-realtime/dist/leaflet-realtime.js"></script> 
<script src="./index_functions.js"></script--> 
<!--script src="./index.js"></script--> 
<script> 

var map = L.map('map').setView([42, 12], 5);;

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
     maxZoom: 26,
  maxNativeZoom: 19
    
}).addTo(map);

L.control.scale({imperial: false}).addTo(map);

// aggiunta ricerca
map.addControl( new L.Control.Search({
		url: 'https://nominatim.openstreetmap.org/search?format=json&q={s}',
		jsonpParam: 'json_callback',
		propertyName: 'display_name',
		propertyLoc: ['lat','lon'],
		marker: L.circleMarker([0,0],{radius:30}),
		autoCollapse: true,
		autoType: false,
		minLength: 2
	}) );
	
	
	// aggiunto tasto per istruzioni
	var ourCustomControl = L.Control.extend({
 
  options: {
    position: 'topleft' 
    //control position - allowed: 'topleft', 'topright', 'bottomleft', 'bottomright'
  },
 
  onAdd: function (map) {
    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
 
    container.style.backgroundColor = 'white';     
    container.style.backgroundImage = "url(https://upload.wikimedia.org/wikipedia/commons/9/9f/%3Fuestionmark.svg)";
    //container.style.content = "\f000"; 
    //container.style.font.family= "Font Awesome 5 Free";
    container.style.backgroundSize = "30px 30px";
    container.style.width = '30px';
    container.style.height = '30px';
 
    container.onclick = function(){
      alert('Selezionare il  punto di partenza e quello di arrivo su cui far girare il tool per la ricerca del percorso.\
      \n\nNB Per effettuare una ricerca usare il tasto con la lente e digitare \
      il topononimo che si intende cercare.')
      //document.getElementById("myDialog").showModal();
    }
    return container;
  }
 
});


map.addControl(new ourCustomControl());

var popup = L.popup();
	
var marker1;
var marker2;

var greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


var redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


function onMapClick1(e) {
		    document.getElementById('lat1').value = e.latlng.lat.toString();
			document.getElementById('lon1').value = e.latlng.lng.toString();
		
		/*popup
			.setLatLng(e.latlng)
			.setContent("Le coordinate di questo punto sulla mappa sono le seguenti lat:" + e.latlng.lat.toString() +" e lon:"+ e.latlng.lng.toString() +" e sono state automaticamente inserite nel form")
			.openOn(map);*/
			
			popup
			.setLatLng(e.latlng)
			.setContent("Le coordinate di questo punto sulla mappa sono state automaticamente inserite come coordinate del punto di partenza. Cliccare nuovamente per spostare il punto.")
			.openOn(map);
			
			
			//var latlng = e.value.split(',');
	//alert(latlng);
		var lat = e.latlng.lat;
		var lng = e.latlng.lng;
		var zoom = 16;
		setTimeout(function() {
        map.closePopup();
    	}, 10000);
		// add a marker
		if (marker1) { // check
        map.removeLayer(marker1); // remove
    	}
		marker1 = L.marker([lat, lng],{icon: greenIcon}).addTo(map);
			
			
	}
	
function onMapClick2(e) {
		    document.getElementById('lat2').value = e.latlng.lat.toString();
			document.getElementById('lon2').value = e.latlng.lng.toString();
		
		/*popup
			.setLatLng(e.latlng)
			.setContent("Le coordinate di questo punto sulla mappa sono le seguenti lat:" + e.latlng.lat.toString() +" e lon:"+ e.latlng.lng.toString() +" e sono state automaticamente inserite nel form")
			.openOn(map);*/
			
			popup
			.setLatLng(e.latlng)
			.setContent("Le coordinate di questo punto sulla mappa sono state automaticamente inserite come coordinate del punto di arrivo. Cliccare nuovamente per spostare il punto.")
			.openOn(map);
			
			
			//var latlng = e.value.split(',');
	//alert(latlng);
		var lat = e.latlng.lat;
		var lng = e.latlng.lng;
		var zoom = 16;
		setTimeout(function() {
        map.closePopup();
    	}, 10000);
		// add a marker
		if (marker2) { // check
        map.removeLayer(marker2); // remove
    	}
		marker2 = L.marker([lat, lng],{icon: redIcon}).addTo(map);
			
			
	}	
	
	
	
</script>

<script>


(function ($) {
    'use strict';
   
    
    $('[type="radio"][id="input1"]').on('change', function () {
        if ($(this).is(':checked')) {
            //$('#lat1').attr('readonly', true);
            //$('#lon1').attr('readonly', true);
            //$('#lat1').removeAttr('disabled');
            //$('#lon1').removeAttr('disabled');
            $('#lat1').val('');
            $('#lon1').val('');
			var offset = -200; //Offset of 100px
            if (marker1) { // check
        			map.removeLayer(marker1); // remove
    			}
            map.off('click', onMapClick2);
			map.on('click', onMapClick1);
			


            
            return true;
        }
    });  
    


$('[type="radio"][id="input2"]').on('change', function () {
        if ($(this).is(':checked')) {
            //$('#lat2').attr('readonly', true);
            //$('#lon2').attr('readonly', true);
            //$('#lat2').removeAttr('disabled');
            //$('#lon2').removeAttr('disabled');
            $('#lat2').val('');
            $('#lon2').val('');
			var offset = -200; //Offset of 100px
            if (marker2) { // check
        			map.removeLayer(marker2); // remove
    			}
            map.off('click', onMapClick1);
			map.on('click', onMapClick2);
			


            
            return true;
        }
    });

    
    
    
}(jQuery));
</script>
<!--script src="./index_end.js"></script-->
	</body>
</html>
