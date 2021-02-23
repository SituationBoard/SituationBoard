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

export default class StatsWidget extends Widget {

    constructor(frontend, view) {
        super(frontend, view);
    }

    init() {
        this.frontend.registerSocketHandler('stats', (data) => {
            const currentTime = new Date();
            const textYear    = moment(currentTime).format("YYYY");
            const monthIndex  = moment(currentTime).month(); //returns 0 to 11
            const textMonth   = this.language.months[monthIndex];

            $('#statsTotal').text(this.language.textAlarmsTotal);
            $('#statsYear').text(textYear);
            $('#statsMonth').text(textMonth);
            $('#statsToday').text(this.language.textAlarmsToday);

            $('#statsEventsTotal').text(data['total']);
            $('#statsEventsYear').text(data['year']);
            $('#statsEventsMonth').text(data['month']);
            $('#statsEventsToday').text(data['today']);

            $('#statsbox').show();
        });
    }

    update() {
        if(this.settings.standbyShowStatistics){
            this.frontend.socketSend('get_stats');
        }
    }

}