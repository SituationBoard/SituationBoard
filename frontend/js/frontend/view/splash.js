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

export default class SplashView extends View {

    constructor(frontend) {
        super(frontend, ViewPriority.SPLASH, 'splashview');
    }

    init() {
        $('#app_description').hide();
        $('#app_version').hide();
        $('#app_description').text(this.language.textAppDescription);
        $('#app_version').text("Version " + this.frontend.appVersion);
        $('#app_description').fadeIn(1000);
        $('#app_version').fadeIn(1000);

        const splashview = $('#splashview');
        splashview.click((event) => {
            this.hide();
        });
    }

}
