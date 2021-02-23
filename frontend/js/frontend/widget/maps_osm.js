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

import MapsWidget from "/js/frontend/widget/maps.js";

export const MapsOSMGeometries = Object.freeze({
    GEOMETRIES_GEOJSON : "geojson",
    GEOMETRIES_POLYLINE : "polyline"
});

export default class MapsOSMWidget extends MapsWidget {

    constructor(frontend, view, geometries) { // geometries: "geojson" or "polyline"
        super(frontend, view, false); // requiresAPIKey = false

        this.locationMap = null;
        this.routeMap = null;

        this.geometries = geometries;

        this.attributions = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>';
        this.showAttributions = true;

        // default tile server config
        this.tileServerCrossOrigin = 'anonymous';
        this.tileServerMaxNativeZoom = 19.0;
        this.tileServerURLabc = "https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png";
        this.tileServerURLs = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

        if(this.settings.language == "de"){
            this.tileServerCrossOrigin = null;
            this.tileServerMaxNativeZoom = 18.0;
            this.tileServerURLabc = "https://{a-c}.tile.openstreetmap.de/{z}/{x}/{y}.png";
            this.tileServerURLs = "https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png";
        }

        // screenshot tiles (without labels)
        //this.tileServerURLabc = "https://{a-c}.tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png";
        //this.tileServerURLs = "https://{s}.tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png";
    }

    __load() {
        if(this.mapEmergencyLayer != 'none'){
            const url = "https://rawgit.com/tyrasd/osmtogeojson/gh-pages/osmtogeojson.js";
            $.getScript(url, () => {
                this.__init();
            }).fail(() => {
                this.mapEmergencyLayer = 'none';
                this.__init();
            });
        }else{
            this.__init();
        }
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

            if(longitude != 0.0 && latitude != 0.0){
                // location is already known...
                //this.log("OSM Shortcut");
                this.__updateMaps(longitude, latitude);
            }else{
                // ask Nominatim Service where this address is...
                //this.log("OSM Geocoding");
                $.getJSON('http://nominatim.openstreetmap.org/search?format=json&limit=5&q=' + encodeURI(address), (data) => {
                    //this.log(data);
                    if(data != null && Array.isArray(data) && data.length > 0){
                        this.__updateMaps(data[0].lon, data[0].lat);
                    }else{
                        this.error("OSM failed to find address");
                    }
                }).fail(() => {
                    this.error("OSM failed to find address");
                });
            }
        }
    }

    __updateMaps(locationLongitude, locationLatitude) {
        if(this.enableLocationMap){
            this.__updateLocationMap(locationLongitude, locationLatitude);
        }

        if(this.enableRouteMap){
            let homeLongitude = this.settings.mapHomeLongitude;
            let homeLatitude = this.settings.mapHomeLatitude;

            const homeCoordinate     = homeLongitude + "," + homeLatitude;
            const locationCoordinate = locationLongitude + "," + locationLatitude;

            $.getJSON('http://router.project-osrm.org/route/v1/driving/' + homeCoordinate + ';' + locationCoordinate + "?overview=full&geometries=" + this.geometries, (data) => {
                //this.log(data);
                if(data != null && data["code"] == 'Ok' && data["routes"] != null && Array.isArray(data.routes) && data.routes.length > 0) {
                    const route = data;

                    // update start/end location
                    homeLongitude = data.waypoints[0].location[0];
                    homeLatitude = data.waypoints[0].location[1];
                    //locationLongitude = data.waypoints[data.waypoints.length - 1].location[0];
                    //locationLatitude = data.waypoints[data.waypoints.length - 1].location[1];

                    this.__updateRouteMap(homeLongitude, homeLatitude, locationLongitude, locationLatitude, route);
                }else{
                    this.error("OSM failed to calc route");
                }
            }).fail(() => {
                this.error("OSM failed to calc route");
            });
        }
    }

    __getEmergencyObjectQuery(bbox) {
        let nodeQuery = "";

        if(this.mapEmergencyLayer == "all" || this.mapEmergencyLayer == "fire"){
            nodeQuery += 'node["emergency"="fire_hydrant"]["fire_hydrant:type"="pillar"];' +
                         'node["emergency"="fire_hydrant"]["fire_hydrant:type"="underground"];' +
                         'node["emergency"="water_tank"];' +
                         'node["emergency"="suction_point"];' +
                         'node["emergency"="fire_water_pond"];';
        }

        if(this.mapEmergencyLayer == "all" || this.mapEmergencyLayer == "medical" || this.mapEmergencyLayer == "fire"){
            nodeQuery += 'node["emergency"="access_point"];' +
                         'node["emergency"="assembly_point"];' +
                         'node["emergency"="defibrillator"];';
        }

        return '[bbox:' + bbox + '][out:json][timeout:25];(' + nodeQuery + ');out center;>;';
    }

    __getEmergencyObjectMarkerName(properties) {
        let marker = 'hide';

        if(properties["emergency"] == "fire_hydrant"){
            if(properties["fire_hydrant:type"] == "pillar"){
                marker = 'hydrant_pillar';
            }else if(properties["fire_hydrant:type"] == "underground"){
                marker = 'hydrant_underground';
            }
        }else if(properties["emergency"] == "water_tank"){
            marker = 'water_tank';
        }else if(properties["emergency"] == "suction_point"){
            marker = 'suction_point';
        }else if(properties["emergency"] == "fire_water_pond"){
            marker = 'water_pond';
        }else if(properties["emergency"] == "access_point"){
            marker = 'access_point';
        }else if(properties["emergency"] == "assembly_point"){
            marker = 'assembly_point';
        }else if(properties["emergency"] == "defibrillator"){
            marker = 'defibrillator';
        }

        return marker;
    }

}
