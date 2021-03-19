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

export default class Widget {

    constructor(frontend, view) {
        this.frontend = frontend;
        this.view = view;
        this.language = frontend.language;
        this.settings = frontend.settings;
    }

    log(message) {
        this.frontend.log(message);
    }

    warn(message) {
        this.frontend.warn(message);
    }

    error(message) {
        this.frontend.error(message);
    }

    init() { }

    update() { }

}
