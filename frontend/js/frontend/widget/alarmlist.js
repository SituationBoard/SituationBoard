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

import ListWidget from "/js/frontend/widget/list.js";

export default class AlarmListWidget extends ListWidget {

    constructor(frontend, view) {
        super(frontend, view, 'alarmevents');
    }

    init() {
        this.frontend.registerSocketHandler('last_alarm_events', (data) => {
            //this.log("data: " + JSON.stringify(data));=
            const totalEvents = data['total_events'];
            //this.log("totalEvents: " + totalEvents);
            const alarmEvents = jQuery.parseJSON(data['alarm_events']);
            //this.log("alarmEvents: " + JSON.stringify(alarmEvents));

            this.startListUpdate();

            alarmEvents.forEach((alarmEvent) => {
                // create a list entry
                const alarmNumber = totalEvents - this.listEntryCount(); //alarmEvent.eventID;
                const alarmDateTime = moment(alarmEvent.alarmTimestamp);
                const alarmDateString = alarmDateTime.format(this.language.dateFormat + ' – ' + this.language.timeFormatLong);
                const alarmDateWeekday = this.language.weekdays[alarmDateTime.day()];
                let alarmText = '';

                if(alarmEvent.flags == "VALID"){
                    if(alarmEvent.event != "" && alarmEvent.location != ""){
                        alarmText = alarmEvent.event + ', ' + alarmEvent.location;
                    }else{ // either event or location is not set (print the other one only)
                        alarmText = alarmEvent.event + alarmEvent.location;
                    }
                }else{
                    alarmText = this.language.textAlarm;
                }

                this.addListEntry('#' + alarmNumber + ' – ' + alarmDateWeekday + ', ' + alarmDateString, alarmText);
            });

            if(this.listEntryCount() > 0){
                this.finalizeListUpdate();
            }else{
                this.showMessage(this.language.textAlarmHistory, this.language.textNoAlarmEntries);
            }
        });
    }

    update() {
        this.frontend.socketSendParams('get_last_alarm_events', {count: this.settings.maxAlarmEvents});
    }

}
