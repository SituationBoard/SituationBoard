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

import Widget from "/js/frontend/widget/widget.js";

export default class ListWidget extends Widget {

    constructor(frontend, view, listIdentifier) {
        super(frontend, view);
        this.listIdentifier = listIdentifier;
        this.listContentNext = '';
        this.listContentShown = '';
        this.listEntryCountNext = 0;
        this.listEntryCountShown = 0;
    }

    init() {

    }

    update() {

    }

    startListUpdate() {
        this.listContentNext = '';
        this.listEntryCountNext = 0;
    }

    addListEntry(header, body) {
        const entryHTML = '<li><h3>' + header + '</h3>' +
                          '<p>' + body + '</p></li>';
        this.listContentNext = this.listContentNext + entryHTML;
        this.listEntryCountNext = this.listEntryCountNext + 1;
    }

    finalizeListUpdate() {
        if(this.listContentShown != this.listContentNext || this.listEntryCountShown != this.listEntryCountNext){
            this.listContentShown = this.listContentNext;
            this.listEntryCountShown = this.listEntryCountNext;
            $('#' + this.listIdentifier).html('<ul>' + this.listContentShown + '</ul>');
        }
        return this.listEntryCountShown;
    }

    clearList() {
        this.startListUpdate();
        this.finalizeListUpdate();
    }

    listEntryCount() {
        return this.listEntryCountNext;
    }

    listEntryCountShown() {
        return this.listEntryCountShown;
    }

    showMessage(header, message) {
        this.startListUpdate();
        this.addListEntry(header, message);
        this.finalizeListUpdate();
    }

}
