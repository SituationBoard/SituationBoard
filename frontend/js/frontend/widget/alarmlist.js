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

import Widget from "/js/frontend/widget/widget.js";

export default class AlarmListWidget extends Widget {

    constructor(frontend, view) {
        super(frontend, view);
    }

    init() {
        this.frontend.registerSocketHandler('last_alarm_events', (data) => {
            //this.log("LastAlarmEvents: " + JSON.stringify(data));
            let numAlarms = 0;
            let alarmHTML = '';
            // and display next five of them
            const totalEvents = data['total_events'];
            const alarmEvents = jQuery.parseJSON(data['alarm_events']);
            //this.log("LastAlarmEvents: " + JSON.stringify(alarmEvents));
            alarmEvents.forEach((alarmEvent) => {
                if(numAlarms < this.settings.maxAlarmEvents){
                    // create a list item
                    const alarmNumber = totalEvents - numAlarms; //alarmEvent.eventID;
                    const az = moment(alarmEvent.alarmTimestamp).toDate();
                    const azText = moment(az).format(this.language.dateFormat + " – " + this.language.timeFormatLong);
                    const azWeekday = this.language.weekdays[moment(az).day()];
                    let aText = "";

                    if(alarmEvent.flags == "VALID"){
                        if(alarmEvent.event != "" && alarmEvent.location != ""){
                            aText = alarmEvent.event + ', ' + alarmEvent.location;
                        }else{
                            // either event or location is not set (print the other one only)
                            aText = alarmEvent.event + alarmEvent.location;
                        }
                    }else{
                        aText = this.language.textAlarm;
                    }

                    alarmHTML = alarmHTML + '<li><h3>#' + alarmNumber + " – " + azWeekday + ', ' + azText + '</h3>' +
                                            '<p>' + aText + '</p></li>';

                    numAlarms++;
                }
            });
            if(numAlarms == 0){
              alarmHTML = '<li><h3>' + this.language.textAlarmHistory + '</h3>' +
                          '<p>' + this.language.textNoAlarmEntries + '</p></li>';
            }
            //this.log('alarmHTML: ' + alarmHTML);
            $('#alarmevents').html('<ul>' + alarmHTML + '</ul>');
        });
    }

    update() {
        this.frontend.socketSendParams('get_last_alarm_events', {count: this.settings.maxAlarmEvents});
    }

}
