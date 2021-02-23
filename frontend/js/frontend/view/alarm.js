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
/*global moment */

import View, {ViewPriority} from "/js/frontend/view/view.js";
import MapsOSMWidgetOpenLayers from "/js/frontend/widget/maps_osm_openlayers.js";
import MapsOSMWidgetLeaflet from "/js/frontend/widget/maps_osm_leaflet.js";
import MapsGoogleWidget from "/js/frontend/widget/maps_google.js";

export default class AlarmView extends View {

    constructor(frontend) {
        super(frontend, ViewPriority.ALARM, 'alarmview');

        switch(this.settings.mapService){
            case "google":
                this.mapsWidget = new MapsGoogleWidget(frontend, this);
                break;
            case "osm_leaflet":
                this.mapsWidget = new MapsOSMWidgetLeaflet(frontend, this);
                break;
            case "osm_openlayers":
                this.mapsWidget = new MapsOSMWidgetOpenLayers(frontend, this);
                break;
            case "osm":
            default:
                this.mapsWidget = new MapsOSMWidgetOpenLayers(frontend, this);
                this.settings.mapService = "osm";
                break;
        }

        this.alarmTime = 0;
        this.alarmShowtime = 0;
    }

    init() {
        this.frontend.registerSocketHandler('alarm_event', (alarm) => {
            // alarm event -> show alarm view
            this.log('Alarm #' + alarm.eventID + ':\n'
               + 'Timestamp: ' + alarm.timestamp + '\n'
               + 'Event: ' + alarm.event + '\n'
               + 'EventDetails: ' + alarm.eventDetails + '\n'
               + 'Location: ' + alarm.location + '\n'
               + 'LocationDetails: ' + alarm.locationDetails + '\n'
               + 'Comment: ' + alarm.comment + '\n'
               + 'AlarmTimestamp: ' + alarm.alarmTimestamp + '\n'
               + 'LocationLatitude: ' + alarm.locationLatitude + '\n'
               + 'LocationLongitude: ' + alarm.locationLongitude + '\n'
               + 'Source: ' + alarm.source + '\n'
               + 'Sender: ' + alarm.sender + '\n'
               + 'Raw: ' + alarm.raw + '\n'
               + 'Flags: ' + alarm.flags + '\n');

            this.showAlarm(alarm);
        });
    }

    connected() {

    }

    showAlarm(alarm) {
        //TODO: make sure a binary alarm never hides a previous (currently active) text alarm

        this.alarmShowTime = moment(alarm.timestamp).toDate();
        this.alarmTime = moment(alarm.alarmTimestamp).toDate();

        const textDate = moment(this.alarmTime).format(this.language.dateFormat);
        const textTime = moment(this.alarmTime).format(this.language.timeFormatLong);
        const textDateTime = textDate + "\n" + textTime;

        this.mapsWidget.hideAllMaps();

        // update alarmview
        if(alarm.flags == "VALID"){
            // regular text alarm
            $('#event').text(alarm.event);
            $('#eventdetails').text(alarm.eventDetails);
            $('#location').text(alarm.location);
            $('#locationdetails').text(alarm.locationDetails);
            $('#comment').text(alarm.comment);

            $('#raw_fallback').text("");
        }else{
            // invalid alarm or binary alarm
            $('#event').text("");
            $('#eventdetails').text("");
            $('#location').text("");
            $('#locationdetails').text("");
            $('#comment').text("");

            $('#raw_fallback').text(alarm.raw);
        }

        $('#alarmtime').text(textDateTime);
        $('#alarmduration').text("");

        this.show();

        const currentTime = new Date();
        this.cyclic(currentTime);

        if(alarm.flags == "VALID"){
            this.mapsWidget.update(alarm);
        }
    }

    hide() {
        this.mapsWidget.hideAllMaps();
        this.viewManager.hideView(this);
    }

    cyclic(currentTime) {
        if(this.isVisible()){
            // alarm view is visible
            const alarmShowDurationMS = currentTime - this.alarmShowTime;
            if(alarmShowDurationMS > this.settings.alarmDuration * 1000){ // sec -> msec
                // hide alarm view, show and update standby view
                this.hide();
            }else{
                // update alarm view
                const alarmDurationMS = currentTime - this.alarmTime;
                let alarmDurationText = "";
                if(alarmDurationMS < 0){ // Future
                    alarmDurationText = "";
                }else if(alarmDurationMS > 1000 * 60 * 60 * 24){ // Duration > 1 day
                    alarmDurationText = "> 24h";
                }else{
                    const alarmDuration = new moment.utc(alarmDurationMS);
                    alarmDurationText = alarmDuration.format(this.language.timeFormatLong);
                }
                $('#alarmduration').text(alarmDurationText);
            }
        }
    }

}
