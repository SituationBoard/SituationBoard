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

import parseBool from "/js/frontend/util/util.js";

export default class Settings {
    constructor() {
        // tVariables are initialized by render_template from Python code
        this.maxAlarmEvents         = 25;
        this.maxCalendarEntries     = 25;
        this.language               = "{{tLanguage}}";
        this.calendarUpdateDuration = parseInt("{{tCalendarUpdateDuration}}"); // in seconds
        this.alarmDuration          = parseInt("{{tAlarmDuration}}"); // in seconds
        this.alarmShowMaps          = "{{tAlarmShowMaps}}";
        this.standbyShowStatistics  = parseBool("{{tStandbyShowStatistics}}");
        this.standbyShowClock       = parseBool("{{tStandbyShowClock}}");
        this.mapService             = "{{tMapService}}";
        this.mapAPIKey              = "{{tMapAPIKey}}";
        this.mapZoom                = parseFloat("{{tMapZoom}}");
        this.mapType                = "{{tMapType}}";
        this.mapEmergencyLayer      = "{{tMapEmergencyLayer}}";
        this.mapHomeLatitude        = parseFloat("{{tMapHomeLatitude}}");
        this.mapHomeLongitude       = parseFloat("{{tMapHomeLongitude}}");
        this.calendarURL            = "{{tCalendarURL}}"; // iCal URL
        this.pageReloadDuration     = parseInt("{{tPageReloadDuration}}"); // in seconds - necessary only when using Google Maps (because of numerous known internal memory leakage bugs in the Google Maps API)
        this.debug                  = parseBool("{{tDebug}}");
        this.showSplashScreen       = parseBool("{{tShowSplashScreen}}");
    }
}
