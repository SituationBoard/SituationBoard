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
/*global io */
/*global moment */

import Settings from "/js/frontend/util/settings.js";
import * as Languages from "/js/frontend/util/languages.js";

import ViewManager from "/js/frontend/view/viewmanager.js";

import SplashView from "/js/frontend/view/splash.js";
import AlarmView from "/js/frontend/view/alarm.js";
import StandbyView from "/js/frontend/view/standby.js";

const ConnectionState = Object.freeze({
    CONNECTED    : 0,
    DISCONNECTED : 1
});

const SourceState = Object.freeze({
    OK    : 0,
    ERROR : 1
});

export default class Frontend {

    constructor() {
        // tVariables are initialized by render_template from Python code
        this.appVersion        = "{{tVersion}}";
        this.appStartTimestamp = parseInt("{{tStartTimestamp}}");

        this.settings         = new Settings();
        this.viewManager      = new ViewManager();

        this.connectionState  = ConnectionState.DISCONNECTED;
        this.sourceState      = SourceState.ERROR;

        this.socket;
        this.latencyTimes = [];
        this.latencyStartTime;
        this.avgLatency = 0;

        switch(this.settings.language){
            case "de":
                this.language = new Languages.LanguageDE();
                break;
            case "en_us":
                this.language = new Languages.LanguageENus();
                break;
            case "en_gb":
                this.language = new Languages.LanguageENgb();
                break;
            case "en":
            default:
                this.language = new Languages.LanguageEN();
                this.settings.language = "en";
                break;
        }

        this.lastPageReload = new Date();

        this.splashView = new SplashView(this);
        this.viewManager.registerView(this.splashView);

        this.standbyView = new StandbyView(this);
        this.viewManager.registerView(this.standbyView);

        this.alarmView = new AlarmView(this);
        this.viewManager.registerView(this.alarmView);
    }

    log(message) {
        if(this.settings.debug){
            console.log(message);
        }
    }

    warn(message) {
        console.warn(message);
    }

    error(message) {
        console.error(message);
    }

    init() {
        this.cyclic();

        // set timer for cyclic handler
        window.setInterval(() => {
            this.cyclic();
        }, 1000);

        const namespace = '/situationboard';
        const server = location.protocol + '//' + document.domain + ':' + location.port + namespace;

        this.log('Connecting to server ' + server + '...');
        this.socket = io.connect(server);

        this.socket.on('connect', () => {
            this.connectionState = ConnectionState.CONNECTED;
            this.sourceState = SourceState.ERROR;
            this.log('Connected with ' + server);

            this.viewManager.connected();
        });

        this.socket.on('disconnect', () => {
            this.connectionState = ConnectionState.DISCONNECTED;
            this.sourceState = SourceState.ERROR;
            this.error('Disconnected');
        });

        this.registerSocketHandler('state', (state_info) => {
            if(state_info.version != this.appVersion || state_info.start_timestamp != this.appStartTimestamp){
                // backend has been updated or restarted
                // -> reload frontend to get up to date frontend version and configuration
                this.log("Reloading frontend... (backend changed)");
                this._reloadFrontend();
            }

            if(state_info.source_state == "0"){
                this.sourceState = SourceState.OK;
            }else{
                this.sourceState = SourceState.ERROR;
            }

            const latency = (new Date).getTime() - this.latencyStartTime;
            this.latencyTimes.push(latency);
            this.latencyTimes = this.latencyTimes.slice(-30); // keep last 30 samples to calculate average
            let sum = 0;
            for(let i = 0; i < this.latencyTimes.length; i++){
                sum += this.latencyTimes[i];
            }
            this.avgLatency = Math.round(10 * sum / this.latencyTimes.length) / 10;
        });

        // set timer for state handler
        window.setInterval(() => {
            this.latencyStartTime = (new Date).getTime();
            this.socketSend('get_state');
        }, 500);

        this.viewManager.init();
        this.standbyView.show();

        const footer = $('#statusbar');
        footer.css('cursor', 'pointer');
        footer.click(() => {
            this.splashView.showWithTimeout(30000);
        });

        if(this.settings.showSplashScreen){
            this.splashView.showWithTimeout(8000);
        }
    }

    registerSocketHandler(name, handler) {
        this.socket.on(name, handler);
    }

    socketSend(name) {
        this.socket.emit(name);
    }

    socketSendParams(name, message) {
        this.socket.emit(name, message);
    }

    cyclic() {
        const currentTime = new Date();

        this._updateStatusBar(currentTime);

        this.viewManager.cyclic(currentTime);

        if(this.settings.pageReloadDuration > 0){
            const durationMS = currentTime - this.lastPageReload;
            if(durationMS > this.settings.pageReloadDuration * 1000){
                this.lastPageReload = currentTime;
                if(this.viewManager.isVisible(this.alarmView) == false){ // no alarm active
                    this.log("Reloading frontend... (timer)");
                    this._reloadFrontend(); // necessary only when using Google Maps (because of numerous known internal memory leakage bugs in the Google Maps API)
                }
            }
        }
    }

    _reloadFrontend() {
        location.reload(true); // true -> load it from the server (not cache)
    }

    _updateStatusBar(currentTime) {
        let statusText = "";
        if(this.connectionState == ConnectionState.CONNECTED && this.sourceState == SourceState.OK){
            statusText = this.language.textConnected + " – " +
                         this.language.textReceptionOk + " – " +
                         this.language.textLatency + " " + this.avgLatency.toFixed(1) + " " + this.language.textMillisecondsShort;
        }else if(this.connectionState == ConnectionState.CONNECTED){
            statusText = this.language.textConnected + " – " +
                         this.language.textNoReception + " – " +
                         this.language.textLatency + " " + this.avgLatency.toFixed(1) + " " + this.language.textMillisecondsShort;
        }else{
            statusText = this.language.textNotConnected;
        }

        $('#sbstatus').text(statusText);

        const currentDateString = moment(currentTime).format(this.language.dateFormat);
        const currentTimeString = moment(currentTime).format(this.language.timeFormatLong);
        const versionString = "v" + this.appVersion;

        $('#sbtime').text(currentTimeString + " – " + currentDateString + " – SituationBoard " + versionString);

        if(this.connectionState == ConnectionState.CONNECTED && this.sourceState == SourceState.OK){
            $('#statusbar').removeClass('status_error');
            $('#statusbar').addClass('status_ok');
        }else{
            $('#statusbar').removeClass('status_ok');
            $('#statusbar').addClass('status_error');
        }
    }

}

// eslint-disable-next-line no-var
var frontend = new Frontend();

$(document).ready(function(){
    frontend.init();
});
