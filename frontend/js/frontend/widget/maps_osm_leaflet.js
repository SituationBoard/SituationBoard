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
/*global L */
/*global osmtogeojson */

import MapsOSMWidget, {MapsOSMGeometries} from "/js/frontend/widget/maps_osm.js";

export default class MapsOSMWidgetLeaflet extends MapsOSMWidget {

    constructor(frontend, view) {
        super(frontend, view, MapsOSMGeometries.GEOMETRIES_GEOJSON);

        this.emergencyLayer = null;

        this.__loadIfRequired();
    }

    __load() {
        $("<link/>", {
           rel: "stylesheet", type: "text/css",
           href: "https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
        }).appendTo("head");

        $.getScript("https://unpkg.com/leaflet@1.6.0/dist/leaflet.js", () => {
            super.__load();
        });
    }

    hideAllMaps() {
        super.hideAllMaps();

        if(this.emergencyLayer != null){
            this.emergencyLayer = null;
        }

        if(this.locationMap != null){
            this.locationMap.off();
            this.locationMap.remove();
            this.locationMap = null;
        }

        if(this.routeMap != null){
            this.routeMap.off();
            this.routeMap.remove();
            this.routeMap = null;
        }
    }

    __updateLocationMap(locationLongitude, locationLatitude) {
        this.showLocationMap();

        this.locationMap = L.map(this.divLocationMap, {
            center: [locationLatitude, locationLongitude],
            zoom: this.mapZoom,
            zoomControl: false,
            attributionControl: this.showAttributions
        });

        L.tileLayer(this.tileServerURLs, {
            attribution: this.attributions,
            minZoom: this.mapMinZoom,
            maxZoom: this.mapMaxZoom,
            maxNativeZoom: this.tileServerMaxNativeZoom
        }).addTo(this.locationMap);

        if(this.mapEmergencyLayer != 'none'){
            this.__addEmergencyLayer(this.locationMap);
        }
        this.__addMarker(this.locationMap, locationLongitude, locationLatitude, 'marker');
    }

    __updateRouteMap(homeLongitude, homeLatitude, locationLongitude, locationLatitude, route) {
        this.showRouteMap();

        this.routeMap = L.map(this.divRouteMap, {
            center: [locationLatitude, locationLongitude],
            zoom: this.mapZoom,
            zoomControl: false,
            attributionControl: this.showAttributions
        });

        L.tileLayer(this.tileServerURLs, {
            attribution: this.attributions,
            minZoom: this.mapMinZoom,
            maxZoom: this.mapMaxZoom,
            maxNativeZoom: this.tileServerMaxNativeZoom
        }).addTo(this.routeMap);

        const bbox = this.__addRoute(this.routeMap, route);
        this.__addMarker(this.routeMap, homeLongitude, homeLatitude, 'home');
        this.__addMarker(this.routeMap, locationLongitude, locationLatitude, 'marker');
        this.routeMap.fitBounds(bbox);
    }

    __addRoute(map, route, scale = 1.0) {
        const polyline = L.geoJSON(route.routes[0].geometry, {
            weight: 8 * scale,
            color: 'rgba(167, 41, 32, 0.8)'
        }).addTo(map);
        const bbox = polyline.getBounds();
        return bbox;
    }

    __addEmergencyLayer(map) {
        const stringExtent = map.getBounds().getSouth() + ',' + map.getBounds().getWest() + ',' +
                           map.getBounds().getNorth() + ',' + map.getBounds().getEast();
        const query = this.__getEmergencyObjectQuery(stringExtent);
        fetch('https://overpass-api.de/api/interpreter', { method: "POST", body: query })
        .then(response => response.json())
        .then(json => {
            const resultAsGeojson = osmtogeojson(json, { flatProperties: true });
            if(this.emergencyLayer){
                //this.log("updating geojson layer...");
                this.emergencyLayer.addData(resultAsGeojson);
            }else{
                //this.log("adding geojson layer...");
                this.emergencyLayer = L.geoJson(resultAsGeojson, {
                    pointToLayer: (feature, latlng) => { return this.__getEmergencyObjectStyle(feature, latlng); },
                    filter: (feature, layer) => {
                        const isPolygon = (feature.geometry) && (feature.geometry.type !== undefined) && (feature.geometry.type === "Polygon");
                        if(isPolygon){
                            feature.geometry.typed = "Point";
                            const polygonCenter = L.latLngBounds(feature.geometry.coordinates[0]).getCenter();
                            feature.geometry.coordinates = [ polygonCenter.lat, polygonCenter.lng ];
                        }
                        return true;
                    }
                }).addTo(map);
                map.on('moveend', () => { this.__addEmergencyLayer(this.locationMap); });
                map.on('zoomend', () => { this.__addEmergencyLayer(this.locationMap); });
            }
        })
        .catch(() => { });
    }

    __getEmergencyObjectStyle(feature, latlng) {
        //this.log(feature);
        const marker = this.__getEmergencyObjectMarkerName(feature.properties);
        const markerIcon = this.__getMarker(marker);
        return L.marker(latlng, {icon: markerIcon});
    }

    __getMarker(marker, scale = 1.0) {
        const markerImage = this.markerImages[marker];
        const markerIcon = new L.Icon({
            iconUrl: markerImage.url,
            iconSize: [markerImage.size[0] * markerImage.prescale * scale,
                       markerImage.size[1] * markerImage.prescale * scale],
            iconAnchor: [markerImage.anchor[0] * markerImage.size[0] * markerImage.prescale * scale,
                         markerImage.anchor[1] * markerImage.size[1] * markerImage.prescale * scale],
        });
        return markerIcon;
    }

    __addMarker(map, longitude, latitude, marker, scale = 1.0) {
        const markerIcon = this.__getMarker(marker, scale);
        L.marker([latitude, longitude], { icon: markerIcon }).addTo(map);
    }

    __layoutChanged() {
        if(this.locationMap){
            //console.log('resized location map');
            this.locationMap.invalidateSize();
        }

        if(this.routeMap){
            //console.log('resized route map');
            this.routeMap.invalidateSize();
        }
    }

}