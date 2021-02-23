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

import Widget from "/js/frontend/widget/widget.js";

export default class MapsWidget extends Widget {

    constructor(frontend, view, requiresAPIKey) {
        super(frontend, view);

        this.markerImages = {
            hide:                {url: "img/hide.png",           size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.3},
            marker:              {url: "img/marker.png",         size: [128, 256],   anchor: [0.5, 1.0],  prescale: 0.3},
            //home:                {url: "img/home.png",           size: [128, 256],   anchor: [0.5, 1.0],  prescale: 0.3},
            home:                {url: "img/home_dot.png",       size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.15},
            hydrant_pillar:      {url: "img/pillar.png",         size: [128, 256],   anchor: [0.5, 0.75], prescale: 0.2},
            hydrant_underground: {url: "img/underground.png",    size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.2},
            water_tank:          {url: "img/tank.png",           size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.2},
            suction_point:       {url: "img/tank.png",           size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.2},
            water_pond:          {url: "img/tank.png",           size: [128, 128],   anchor: [0.5, 0.5],  prescale: 0.2},
            access_point:        {url: "img/assembly_point.png", size: [1024, 1024], anchor: [0.5, 0.5],  prescale: 0.03},
            assembly_point:      {url: "img/assembly_point.png", size: [1024, 1024], anchor: [0.5, 0.5],  prescale: 0.03},
            defibrillator:       {url: "img/defibrillator.png",  size: [1024, 1024], anchor: [0.5, 0.5],  prescale: 0.03}
        };

        this.requiresAPIKey = requiresAPIKey;

        this.enableMaps = false;
        this.enableLocationMap = false;
        this.enableRouteMap = false;

        this.mapType = 'default';
        this.mapEmergencyLayer = 'none';

        this.mapMinZoom     = 1.0;
        this.mapMaxZoom     = 20.0;
        this.mapDefaultZoom = 19.0;

        this.mapZoom = this.mapDefaultZoom;

        this.divAlarmMaps   = "alarmmaps";
        this.divAlarmInfo   = "alarminfo";
        this.divLocationMap = "alarmlocationmap";
        this.divRouteMap    = "alarmroutemap";

        if(this.settings.alarmShowMaps != "none"){
            if(this.requiresAPIKey == false || this.settings.mapAPIKey != ""){
                if(this.settings.alarmShowMaps == "both" || this.settings.alarmShowMaps == "location"){
                    this.enableLocationMap = true;
                    this.mapEmergencyLayer = this.settings.mapEmergencyLayer;
                }

                if((this.settings.alarmShowMaps == "both" || this.settings.alarmShowMaps == "route") &&
                   (this.settings.mapHomeLatitude != 0.0 || this.settings.mapHomeLongitude != 0.0)){
                    this.enableRouteMap = true;
                }

                if(this.settings.mapZoom < 0.0){
                    this.mapZoom = this.mapDefaultZoom;
                }else{
                    if(this.settings.mapZoom < this.mapMinZoom){
                        this.mapZoom = this.mapMinZoom;
                    }else if(this.settings.mapZoom > this.mapMaxZoom){
                        this.mapZoom = this.mapMaxZoom;
                    }else{
                        this.mapZoom = this.settings.mapZoom;
                    }
                }
            }
        }
    }

    update(alarm) { }

    __loadIfRequired() {
        if(this.enableLocationMap || this.enableRouteMap){
            this.__load();
        }
    }

    __load() {
        // should either call __init() or set enableMaps to true directly (after successful completion)
    }

    __init() {
        this.enableMaps = true;
    }

    showLocationMap() {
        $('#' + this.divLocationMap).show();
        $('#' + this.divAlarmMaps).show();
        $('#' + this.divAlarmInfo).addClass('maps_visible');
        this.__layoutChanged();
    }

    showRouteMap() {
        $('#' + this.divRouteMap).show();
        $('#' + this.divAlarmMaps).show();
        $('#' + this.divAlarmInfo).addClass('maps_visible');
        this.__layoutChanged();
    }

    hideAllMaps() {
        //console.log("hideAllMaps");
        $('#' + this.divAlarmMaps).hide();
        $('#' + this.divLocationMap).hide();
        $('#' + this.divRouteMap).hide();
        $('#' + this.divAlarmInfo).removeClass('maps_visible');
    }

    __layoutChanged() { }

}