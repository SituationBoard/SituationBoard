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

import View, {ViewPriority} from "/js/frontend/view/view.js";
import StatsWidget from "/js/frontend/widget/stats.js";
import AlarmListWidget from "/js/frontend/widget/alarmlist.js";
import ClockWidget from "/js/frontend/widget/clock.js";
import CalendarWidget from "/js/frontend/widget/calendar.js";

export default class StandbyView extends View {

    constructor(frontend) {
        super(frontend, ViewPriority.STANDBY, 'standbyview');

        this.dataHeader = "";
        this.dataNews   = "";

        this.statsWidget     = new StatsWidget(frontend, this);
        this.alarmListWidget = new AlarmListWidget(frontend, this);
        this.clockWidget     = new ClockWidget(frontend, this);
        this.calendarWidget  = new CalendarWidget(frontend, this);

        const timestamp = new Date();

        this.lastDate = timestamp;
        this.lastCalendarUpdate = timestamp;
    }

    init() {
        this.statsWidget.init();
        this.alarmListWidget.init();
        this.clockWidget.init();
        this.calendarWidget.init();

        this.frontend.registerSocketHandler('news', (data) => {
            this.dataNews = data['news'];
            $('#news').text(this.dataNews);
        });

        this.frontend.registerSocketHandler('header', (data) => {
            this.dataHeader = data['header'];
            $('#header').text(this.dataHeader);
        });

        this.frontend.registerSocketHandler('database_changed', (data) => {
            // Ignored for now - we update alarm list and stats in becomesVisible()
        });

        this.frontend.registerSocketHandler('calendar_changed', (data) => {
            this.log("Updating calendar... (backend event)");
            this.lastCalendarUpdate = new Date();
            this.calendarWidget.update();
        });
    }

    connected() {
        this._updateHeader();
        this._updateNews();

        this.alarmListWidget.update();
        this.statsWidget.update();
    }

    becomesVisible() {
        this.alarmListWidget.update();
        this.statsWidget.update();
    }

    cyclic(currentTime) {
        this.clockWidget.update(currentTime);

        if(this.lastDate.toDateString() != currentTime.toDateString()){
            //new day
            this.lastDate = currentTime;
            this.log("Updating statistics... (new day)");
            this.statsWidget.update();
            this.log("Updating calendar... (new day)");
            this.calendarWidget.update();
        }

        if(this.settings.calendarUpdateDuration > 0){
            const durationMS = currentTime - this.lastCalendarUpdate;
            if(durationMS > this.settings.calendarUpdateDuration * 1000){
                this.lastCalendarUpdate = currentTime;
                this.log("Updating calendar... (timer)");
                this.calendarWidget.update();
            }
        }
    }

    _updateHeader() {
        this.frontend.socketSend('get_header');
    }

    _updateNews() {
        this.frontend.socketSend('get_news');
    }

}
