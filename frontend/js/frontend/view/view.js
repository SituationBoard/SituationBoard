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

export const ViewPriority = Object.freeze({
    STANDBY  : 0,
    SPLASH   : 1,
    ALARM    : 2
});

export default class View {

    constructor(frontend, priority, elementID = "") {
        this.frontend = frontend;
        this.viewManager = frontend.viewManager;
        this.language = frontend.language;
        this.settings = frontend.settings;
        this.priority = priority;
        this.timeout = null;
        if(elementID != ""){
            this.elementID = elementID;
            this.element = $('#' + this.elementID);
        }else{
            this.elementID = "";
            this.element = null;
        }
    }

    log(message) {
        this.frontend.log(message);
    }

    error(message) {
        this.frontend.error(message);
    }

    show() {
        this._cancelTimeout();
        this.viewManager.showView(this);
    }

    showWithTimeout(timeout) {
        this._cancelTimeout();
        this.show();

        this.timeout = window.setTimeout(() => {
            this.viewManager.hideView(this);
        }, timeout);
    }

    hide() {
        this._cancelTimeout();
        this.viewManager.hideView(this);
    }

    _cancelTimeout() {
        if(this.timeout != null){
            window.clearTimeout(this.timeout);
            this.timeout = null;
        }
    }

    isActive() {
        return this.viewManager.isActive(this);
    }

    isVisible() {
        return this.viewManager.isVisible(this);
    }

    doShow() {
        if(this.element != null){
            this.element.show();
        }else{
            this.error("view.doShow() without element");
        }
    }

    doHide() {
        if(this.element != null){
            this.element.hide();
        }else{
            this.error("view.doHide() without element");
        }
    }

    init() { }

    connected() { }

    becomesVisible() { }

    becomesHidden() { }

    cyclic(currentTime) { }

}
