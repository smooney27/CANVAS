function StreetviewService() { 
  return {
    initialize: function(start_lat, start_lng, end_lat, end_lng, pano_element, map, pano_callback, date_callback){
      var requested_location = new google.maps.LatLng(start_lat, start_lng);
      var lat_change = end_lat - start_lat;
      var lng_change = end_lng - start_lng;
      var road_direction_rad = Math.atan2(lng_change, lat_change);
      // +45 is to turn 45 degrees to the right
//      var heading = ((road_direction_rad) * 360 / (2 * Math.PI)) + 45;
      var heading = ((road_direction_rad) * 360 / (2 * Math.PI));
      var sv = new google.maps.StreetViewService();
      var location_callback = function(data, status){
        if (status == "ZERO_RESULTS") {
          pano_element.innerHTML = 'No Street View found for this location';
        } else {
          var location = data.location.latLng;
          var panoramaOptions = {
            position: location,
            pov: {
              heading: heading,
              pitch: 0,
              zoom: 1
            }
          };
          
          var pano = new google.maps.StreetViewPanorama(pano_element, panoramaOptions);
          pano.setPano(data.location.pano);
          if (typeof(map) != 'undefined' && map != null) {
            map.setStreetView(pano);
          }
          if (typeof(pano_callback) != 'undefined') {
            pano_callback(pano);
          }
          if (typeof(date_callback) != 'undefined') {
            date_callback(data.imageDate);
          }

          // Hack added 3/24 to reset streetview zoom to level 1 if it drops to level 0.
          var fix_zoom = function(pano, timeout) {
            var pov = pano.getPov();
            if (pov.zoom < 1) {
              pov.zoom = 1;
              pano.setPov(pov);
            }
            setTimeout(function(pano, timeout){return function(){fix_zoom(pano, timeout);};}(pano, timeout), timeout);
          }
          fix_zoom(pano, 1000);
        }
      }
      var panorama = sv.getPanoramaByLocation(requested_location, 50, location_callback);
      return panorama;
    },
    initialize_for_addresses: function(street_address, pano_element){
      var geocoder = new google.maps.Geocoder();
      geocoder.geocode({address:street_address}, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
          var address_location = results[0].geometry.location
          var streetview_service = new StreetviewService();
          streetview_service.initialize(address_location.lat(), address_location.lng(), address_location.lat(), address_location.lng(), pano_element);
        } else {
          pano_element.innerHTML = "Could not get lat/lng for address for the following reason: " + status;
        }
      });
    },
    open_pano_window:function(url) {
      var pano_window = window.open('', 'pano_window', 'location=0,width=800,height=800');
      if (pano_window.location != url) {
        pano_window.location = url;
      }
      return pano_window;
    },
    km_to_degrees: function(distance, current_lat) {
      var circumference = 40075
      if (current_lat != null) {
        var circumference = circumference*Math.cos(current_lat*(2*Math.PI/360));
      } 
      var degrees = distance*360/circumference; 
      return degrees;
    }
  }
}
g_streetview_service = new StreetviewService();

