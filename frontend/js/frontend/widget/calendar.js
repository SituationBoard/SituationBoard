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
/*global rrule */

import ListWidget from "/js/frontend/widget/list.js";

export default class CalendarWidget extends ListWidget {

    constructor(frontend, view) {
        super(frontend, view, 'calendarevents');
        this.fileData = null;
    }

    init() {
        this.update();
    }

    __createEvent(title, start, end, duration, allday) {
        const e = {};
        e['title'] = title;
        e['start'] = start;
        e['end'] = end;
        e['duration'] = duration;
        e['allday'] = allday;
        return e;
    }

    // The following helper function is based on the iCal.js rrule example:
    // https://github.com/peterbraden/ical.js/blob/master/example_rrule.js
    __getEvents(fileData, maxEvents=-1, days=365) {
        const data = ical.parseICS(fileData);

        const nowDate = moment();
        const rangeStart = nowDate.clone();
        const rangeEnd = rangeStart.clone().add(days, 'days');

        const expandedEvents = [];

        for(const k in data){
            if(Object.prototype.hasOwnProperty.call(data, k)){
                const event = data[k];

                if(event.type === 'VEVENT'){
                    const title = event.summary;
                    let startDate = moment(event.start);
                    let endDate = moment(event.end);

                    const allday = event.start.dateOnly !== undefined && event.start.dateOnly;

                    const duration = parseInt(endDate.format("x")) - parseInt(startDate.format("x"));

                    if(typeof event.rrule === 'undefined'){
                        const e = this.__createEvent(title, startDate, endDate, duration, allday);
                        expandedEvents.push(e);
                    }else if(typeof event.rrule !== 'undefined'){
                        const eventRRule = rrule.rrulestr(event.rrule, { dtstart: startDate.toDate() });
                        const dates = eventRRule.between(rangeStart.toDate(), rangeEnd.toDate(), true, (date, i) => true);

                        if(event.recurrences != undefined){
                            for(const r in event.recurrences){
                                if(moment(new Date(r)).isBetween(rangeStart, rangeEnd) != true){
                                    dates.push(new Date(r));
                                }
                            }
                        }

                        for(const i in dates) {
                            const date = dates[i];
                            let curEvent = event;
                            let addRecurrence = true;
                            let curDuration = duration;

                            startDate = moment(date);

                            const dateLookupKey = date.toISOString().substring(0, 10);

                            if((curEvent.recurrences != undefined) && (curEvent.recurrences[dateLookupKey] != undefined)){
                                curEvent = curEvent.recurrences[dateLookupKey];
                                startDate = moment(curEvent.start);
                                curDuration = parseInt(moment(curEvent.end).format("x")) - parseInt(startDate.format("x"));
                            }else if((curEvent.exdate != undefined) && (curEvent.exdate[dateLookupKey] != undefined)){
                                addRecurrence = false;
                            }

                            const recurrenceTitle = curEvent.summary;
                            endDate = moment(parseInt(startDate.format("x")) + curDuration, 'x');

                            if(endDate.isBefore(rangeStart) || startDate.isAfter(rangeEnd)) {
                                addRecurrence = false;
                            }

                            if(addRecurrence === true) {
                                const e = this.__createEvent(recurrenceTitle, startDate, endDate, curDuration, allday);
                                expandedEvents.push(e);
                            }
                        }
                    }
                }
            }
        }

        // only show events that are in the future (or ongoing) ...
        const eventsFiltered = expandedEvents.filter(event => event['start'].isAfter(nowDate) || event['end'].isAfter(nowDate));

        // sort events (earliest event first) ...
        const sortedEvents = eventsFiltered.sort((eventA, eventB) => eventA['start'].valueOf() - eventB['start'].valueOf());

        if(maxEvents > 0){
            sortedEvents.splice(maxEvents);
        }

        return sortedEvents;
    }

    __updateList(){
        const events = this.__getEvents(this.fileData, this.settings.maxCalendarEntries);

        this.startListUpdate();

        events.forEach((calendarEvent) => {
            // add a list entry
            let eventDateString = '';
            if(calendarEvent['allday']){
                eventDateString = calendarEvent['start'].format(this.language.dateFormat);
            }else{
                eventDateString = calendarEvent['start'].format(this.language.dateFormat + ' – ' + this.language.timeFormatShort);
            }
            const eventWeekday = this.language.weekdays[calendarEvent['start'].day()];
            this.addListEntry(eventWeekday + ', ' + eventDateString, calendarEvent['title']);
        });

        if(this.listEntryCount() > 0){
            this.finalizeListUpdate();
        }else{
            this.showMessage(this.language.textCalendar, this.language.textNoCalendarEntries);
        }
    }

    update(forceReload = true) {
        if(this.settings.calendarURL == ""){
            // this.warn("No calendar configured");
            this.showMessage(this.language.textCalendar, this.language.textNoCalendarError);
        }else if(forceReload || this.fileData === null){
            //this.log("calendar update (reload)");
            $.get(this.settings.calendarURL)
            .done(newFileData => {
                this.fileData = newFileData;
                this.__updateList();
            })
            .fail((err) => {
                // this.warn("No calendar available");
                this.showMessage(this.language.textCalendar, this.language.textNoCalendarError);
            });
        }else{
            //this.log("calendar update (list only)");
            this.__updateList();
        }
    }

}
