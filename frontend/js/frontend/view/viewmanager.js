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

export default class ViewManager {

    constructor() {
        this.registeredViews = [];
        this.waitingViews = []; //TODO: use a priority queue here
        this.activeView = null;
    }

    registerView(view) {
        if(this.registeredViews.includes(view)){
            return;
        }

        this.registeredViews.push(view);
    }

    unregisterView(view) {
        const index = this.registeredViews.indexOf(view);
        if(index > -1){
            this.registeredViews.splice(index, 1);
        }
    }

    init() {
        for(const view of this.registeredViews){
            view.init();
        }
    }

    connected() {
        for(const view of this.registeredViews){
            view.connected();
        }
    }

    cyclic(time) {
        for(const view of this.registeredViews){
            view.cyclic(time);
        }
    }

    _getWaitingViewWithHighestPriority() {
        let vHighestPriority = null;
        for(const vCurrent of this.waitingViews){
            if(vHighestPriority == null || vCurrent.priority > vHighestPriority.priority){
                vHighestPriority = vCurrent;
            }
        }
        return vHighestPriority;
    }

    _removeWaitingView(view) {
        const index = this.waitingViews.indexOf(view);
        if(index > -1){
            this.waitingViews.splice(index, 1);
        }
    }

    showView(view) {
        if(this.activeView == view){
            // New view is already active
            return;
        }else if(this.activeView != null){
            if(view.priority > this.activeView.priority){
                // New view has higher priority than active view
                // -> hide old one and show new one
                this.activeView.becomesHidden();
                this.activeView.doHide();
                this.waitingViews.push(this.activeView);
                this.activeView = view;
                view.becomesVisible();
                view.doShow();
            }else{
                // View has lower priority than active view
                // -> append it to the view stack
                if(this.waitingViews.includes(view)){
                    // View is already in the view stack
                    return;
                }
                this.waitingViews.push(view);
            }
        }else{
            // There was no view active before -> activate new one
            this.activeView = view;
            view.becomesVisible();
            view.doShow();
        }
    }

    hideView(view) {
        if(this.activeView != view){
            // the view is not the active view
            // -> only remove it from the view stack
            this._removeWaitingView(view);
        }else{
            // the view is the active view
            this.activeView.becomesHidden();
            this.activeView.doHide();
            const vHighestPriority = this._getWaitingViewWithHighestPriority();
            if(vHighestPriority != null){
                // found next view (with the highest priority)
                // -> switch to view with the next highest priority
                this._removeWaitingView(vHighestPriority);
                this.activeView = vHighestPriority;
                vHighestPriority.becomesVisible();
                vHighestPriority.doShow();
            }else{
                // no next view found
                this.activeView = null;
            }
        }
    }

    isActive(view) {
        return (this.activeView == view);
    }

    isVisible(view) {
        if(this.activeView == view){
            return true;
        }

        return this.waitingViews.includes(view);
    }

}
