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
/*global ol */
/*global osmtogeojson */

import MapsOSMWidget, {MapsOSMGeometries} from "/js/frontend/widget/maps_osm.js";

export default class MapsOSMWidgetOpenLayers extends MapsOSMWidget {

    constructor(frontend, view) {
        super(frontend, view, MapsOSMGeometries.GEOMETRIES_POLYLINE);

        this.__loadIfRequired();
    }

    __load() {
        $("<link/>", {
           rel: "stylesheet", type: "text/css",
           href: "https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.3.1/css/ol.css"
        }).appendTo("head");

        $.getScript("https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.3.1/build/ol.js", () => {
            // adjust attributions size and style
            $(`<style>
                .ol-attribution {
                    font-size: 11px;
                }
                .ol-attribution a {
                    color: #0078A8;
                    text-decoration: none;
                }
                .ol-attribution a:hover {
                    text-decoration: underline;
                }
            </style>`).appendTo("head");

            super.__load();
        });
    }

    hideAllMaps() {
        super.hideAllMaps();

        if(this.locationMap != null){
            this.locationMap.setTarget(null);
            this.locationMap = null;
        }

        if(this.routeMap != null){
            this.routeMap.setTarget(null);
            this.routeMap = null;
        }
    }

    __updateLocationMap(locationLongitude, locationLatitude) {
        this.showLocationMap();

        this.locationMap = new ol.Map({
            target: this.divLocationMap,
            controls: ol.control.defaults({ attribution: this.showAttributions, zoom: false }),
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM({
                        crossOrigin: this.tileServerCrossOrigin,
                        url: this.tileServerURLabc,
                        attributions: this.attributions
                    })
                })
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([locationLongitude, locationLatitude]),
                zoom: this.mapZoom
            })
        });

        if(this.mapEmergencyLayer != 'none'){
            this.__addEmergencyLayer(this.locationMap);
        }
        this.__addMarker(this.locationMap, locationLongitude, locationLatitude, 'marker');
    }

    __updateRouteMap(homeLongitude, homeLatitude, locationLongitude, locationLatitude, route) {
        this.showRouteMap();

        const polyline = route.routes[0].geometry;
        const routeLine = new ol.format.Polyline({
            factor: 1e5
        }).readGeometry(polyline, {
            dataProjection: 'EPSG:4326',
            featureProjection: 'EPSG:3857'
        });

        const view = new ol.View({
            center: ol.proj.fromLonLat([homeLongitude, homeLatitude]),
            zoom: this.mapZoom
        });

        this.routeMap = new ol.Map({
            target: this.divRouteMap,
            controls: ol.control.defaults({ attribution: this.showAttributions, zoom: false }),
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM({
                        crossOrigin: this.tileServerCrossOrigin,
                        url: this.tileServerURLabc,
                        attributions: this.attributions
                    })
                })
            ],
            view: view
        });

        this.__addRoute(this.routeMap, routeLine);
        this.__addMarker(this.routeMap, homeLongitude, homeLatitude, 'home');
        this.__addMarker(this.routeMap, locationLongitude, locationLatitude, 'marker');
        view.fit(routeLine, {padding: [100, 100, 100, 100]});
    }

    __addRoute(map, route, scale = 1.0) {
        const feature = new ol.Feature({
            type: 'route',
            geometry: route
        });

        feature.setStyle(new ol.style.Style({
            stroke: new ol.style.Stroke({
                width: 8 * scale,
                color: [167, 41, 32, 0.8]
            })
        }));

        map.addLayer(new ol.layer.Vector({
            source: new ol.source.Vector({ features: [ feature ] })
        }));
    }

    __addEmergencyLayer(map) {
        const vectorSource = new ol.source.Vector({
            format: new ol.format.GeoJSON(),
            loader: (extent, resolution, projection) => {
                const epsg4326Extent = ol.proj.transformExtent(extent, projection, 'EPSG:4326');
                const stringExtent = epsg4326Extent[1] + ',' + epsg4326Extent[0] + ',' +
                                   epsg4326Extent[3] + ',' + epsg4326Extent[2];
                const query = this.__getEmergencyObjectQuery(stringExtent);
                fetch('https://overpass-api.de/api/interpreter', { method: "POST", body: query })
                .then(response => response.json())
                .then(json => {
                    const geojson = osmtogeojson(json, { flatProperties: true });
                    const features = new ol.format.GeoJSON().readFeatures(geojson, {
                        featureProjection: map.getView().getProjection()
                    });
                    vectorSource.addFeatures(features);
                })
                .catch(() => { });
            },
            strategy: ol.loadingstrategy.bbox
        });

        map.addLayer(new ol.layer.Vector({
            renderMode: 'image',
            style: (feature, resolution) => { return this.__getEmergencyObjectStyle(feature, resolution); },
            source: vectorSource
        }));
    }

    __getEmergencyObjectStyle(feature, resolution) {
        //this.log(feature);
        //this.log(resolution);
        const marker = this.__getEmergencyObjectMarkerName(feature.values_);
        return this.__getMarker(marker);
    }

    __getMarker(marker, scale = 1.0) {
        const markerImage = this.markerImages[marker];
        const style = new ol.style.Style({
            image: new ol.style.Icon({
                anchor: markerImage.anchor,
                src: markerImage.url,
                scale: markerImage.prescale * scale
            })
        });
        return style;
    }

    __addMarker(map, longitude, latitude, marker, scale = 1.0) {
        const markerStyle = this.__getMarker(marker, scale);

        const feature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat([longitude, latitude]))
        });

        feature.setStyle(markerStyle);

        map.addLayer(new ol.layer.Vector({
            source: new ol.source.Vector({ features: [ feature ] })
        }));
    }

    __layoutChanged() {
        if(this.locationMap != null){
            //console.log('resized location map');
            this.locationMap.updateSize();
        }

        if(this.routeMap != null){
            //console.log('resized route map');
            this.routeMap.updateSize();
        }
    }

}