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
/*global ical */

import Widget from "/js/frontend/widget/widget.js";

export default class CalendarWidget extends Widget {

    constructor(frontend, view) {
        super(frontend, view);
    }

    init() {
        this.update();
    }

    update() {
        if(this.settings.calendarURL == ""){
            this.error(this.language.textNoCalendarError);
        }else{
            $.get(this.settings.calendarURL)
            .done(fileData => {
                const data = ical.parseICS(fileData);

                let numEvents = 0;
                let eventHTML = '';
                const nowDate = moment();

                for(const k in data){
                    if(Object.prototype.hasOwnProperty.call(data, k)){
                        const event = data[k];
                        if(data[k].type == 'VEVENT'){
                            const eventTitle = event.summary;
                            const eventStartDate = moment(event.start);
                            const eventEndDate = moment(event.end);

                            if(typeof event.rrule === 'undefined'){
                                // only show events that are in the future...
                                if(eventStartDate >= nowDate || eventEndDate >= nowDate){
                                    if(numEvents < this.settings.maxCalendarEntries){
                                        numEvents++;
                                        // create a list item
                                        const eventDateString = eventStartDate.format(this.language.dateFormat + " – " + this.language.timeFormatShort);
                                        const eventWeekday = this.language.weekdays[eventStartDate.day()];
                                        eventHTML = eventHTML + '<li><h3>' + eventWeekday + ', ' + eventDateString + '</h3>' +
                                                                '<p>' + eventTitle + '</p></li>';
                                    }
                                }
                            }else if(typeof event.rrule !== 'undefined'){
                                //TODO: handle recurring events
                            }
                        }
                    }
                }

                if(numEvents != 0){
                    $('#calendarevents').html('<ul>' + eventHTML + '</ul>');
                }else{
                    this.error(this.language.textNoCalendarEntries);
                }
            })
            .fail((err) => {
                this.error(this.language.textNoCalendarError);
            });
        }
    }

    error(message) {
        const messageHTML = '<li><h3>' + this.language.textCalendar + '</h3>' +
                          '<p>' + message + '</p></li>';
        $('#calendarevents').html('<ul>' + messageHTML + '</ul>');
    }

}