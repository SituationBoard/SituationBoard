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

export default class ClockWidget extends Widget {

    constructor(frontend, view) {
        super(frontend, view);
    }

    update(currentTime) {
        if(this.settings.standbyShowClock){
            const currentDateString = moment(currentTime).format(this.language.dateFormat);
            const currentTimeString = moment(currentTime).format(this.language.timeFormatLong);
            const currentWeekdayString = this.language.weekdaysShort[moment(currentTime).day()];
            $('#clocktime').text(currentTimeString);
            $('#clockdate').text(currentWeekdayString + ", " + currentDateString);
            $('#clockbox').show();
        }
    }

}