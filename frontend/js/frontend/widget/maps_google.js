/*
SituationBoard - Alarm Display for Fire Departments
Copyright (C) 2017-2021 Sebastian Maier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

"use strict";
/*global google */
/*_global frontend */

import MapsWidget from "/js/frontend/widget/maps.js";

// called after the browser loaded the Google Maps API asynchronously
//function initMapsGoogle(){ // eslint-disable-line no-unused-vars
//    frontend.alarmView.mapsWidget.__init();
//}

export default class MapsGoogleWidget extends MapsWidget {

    constructor(frontend, view) {
        super(frontend, view, true); // requiresAPIKey = true

        this.mapHomeLocation      = null;
        this.mapAlarmLocation     = null;
        this.mapGeocoder          = null;
        this.mapMarker            = null;
        this.mapDirectionsDisplay = null;
        this.mapDirectionsService = null;
        this.mapAlarmLocationMap  = null;
        this.mapAlarmRouteMap     = null;

        if(this.settings.mapType == 'default'){
            this.mapType = 'hybrid';
        }else{
            this.mapType = this.settings.mapType;
        }

        this.__loadIfRequired();
    }

    __load() {
        const key = this.settings.mapAPIKey;
        //const callback = "initMapsGoogle";
        const url = "https://maps.googleapis.com/maps/api/js?key=" + key;// + "&callback=" + callback;
        $.getScript(url, () => {
            // we do not adhere to the Google recommendation (and thus do currently not use the callback parameter)
            this.__init();
        });
    }

    __init() {
        const homeLatitude = this.settings.mapHomeLatitude;
        const homeLongitude = this.settings.mapHomeLongitude;

        // init home location
        this.mapHomeLocation = new google.maps.LatLng(homeLatitude, homeLongitude);
        // init geocoder
        this.mapGeocoder = new google.maps.Geocoder();

        if(this.enableLocationMap){
            // init location map
            this.mapAlarmLocationMap = new google.maps.Map(document.getElementById(this.divLocationMap), {
                center: this.mapHomeLocation,
                scrollwheel: false,
                disableDefaultUI: true,
                mapTypeId: this.mapType,
                zoom: this.mapZoom
            });

            // init location marker
            this.mapMarker = new google.maps.Marker({
                map: this.mapAlarmLocationMap,
                position: this.mapHomeLocation
            });
        }

        if(this.enableRouteMap){
            // init route map
            this.mapAlarmRouteMap = new google.maps.Map(document.getElementById(this.divRouteMap), {
                center: this.mapHomeLocation,
                scrollwheel: false,
                disableDefaultUI: true,
                mapTypeId: this.mapType,
                zoom: this.mapZoom
            });

            // init direction service and renderer
            this.mapDirectionsService = new google.maps.DirectionsService();
            this.mapDirectionsDisplay = new google.maps.DirectionsRenderer();
            this.mapDirectionsDisplay.setMap(this.mapAlarmRouteMap);
        }

        this.enableMaps = true;
    }

    update(alarm) {
        if(this.enableMaps){
            let latitude = 0.0;
            let longitude = 0.0;
            let address = "";

            if(alarm.locationLatitude != 0.0 && alarm.locationLongitude != 0.0){
                latitude = alarm.locationLatitude;
                longitude = alarm.locationLongitude;
            }else if(alarm.location != "" && alarm.locationDetails != ""){
                address = alarm.location + " " + alarm.locationDetails;
            }else{
                return;
            }

            if(latitude != 0.0 && longitude != 0.0){
                // location is already known...
                //this.log("Google Maps Shortcut");
                this.mapAlarmLocation = new google.maps.LatLng(latitude, longitude);
                this.__updateMaps();
            }else{
                // ask Google Geocoding Service where this address is...
                //this.log("Google Maps Geocoding");
                this.mapGeocoder.geocode( {'address': address}, (results, status) => {
                    if(status == google.maps.GeocoderStatus.OK){
                        this.mapAlarmLocation = results[0].geometry.location;
                        this.__updateMaps();
                    }else{
                        this.error("Google Maps failed to find address: " + status);
                    }
                });
            }
        }
    }

    __updateMaps() {
        if(this.mapAlarmLocationMap != null){
            // update alarm location map
            this.showLocationMap();
            this.mapAlarmLocationMap.setCenter(this.mapAlarmLocation);
            this.mapMarker.setPosition(this.mapAlarmLocation);
        }

        if(this.mapAlarmRouteMap != null){
            // trigger calc route to update directions map
            const request = {
                origin: this.mapHomeLocation,
                destination: this.mapAlarmLocation,
                travelMode: google.maps.TravelMode.DRIVING
            };
            this.mapDirectionsService.route(request, (result, status) => {
                if(status == google.maps.DirectionsStatus.OK){
                    // update directions map
                    this.showRouteMap();
                    this.mapDirectionsDisplay.setDirections(result);
                }else{
                    this.error("Google Maps failed to calc route: " + status);
                }
            });
        }
    }

    __layoutChanged() {
        if(this.mapAlarmLocationMap){
            //console.log('resized location map');
            google.maps.event.trigger(this.mapAlarmLocationMap, 'resize'); // refresh / redraw
        }

        if(this.mapAlarmRouteMap){
            //console.log('resized route map');
            google.maps.event.trigger(this.mapAlarmRouteMap, 'resize'); // refresh / redraw
        }
    }

}