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

export default class Language {

    constructor(language) {
        this.language              = language;

        this.months                = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "Novemeber", "December"];
        this.weekdays              = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        this.weekdaysShort         = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        this.dateFormat            = "MM/DD/YYYY";
        this.dateFormatYearOnly    = "YYYY";
        this.timeFormatLong        = "HH:mm:ss";
        this.timeFormatShort       = "HH:mm";

        // invalid alarm
        this.textAlarm             = "Alarm";
        // statistics
        this.textAlarmsTotal       = "Alarms"; // "Total";
        this.textAlarmsToday       = "Today";
        // alarm history
        this.textAlarmHistory      = "Alarm History";
        this.textNoAlarmEntries    = "No alarms yet";
        // calendar
        this.textCalendar          = "Calendar";
        this.textNoCalendarEntries = "No upcoming events";
        this.textNoCalendarError   = "No calendar available";
        // status bar
        this.textConnected         = "Connected";
        this.textNotConnected      = "Not connected!";
        this.textReceptionOk       = "Reception ok";
        this.textNoReception       = "No Reception!";
        this.textLatency           = "Latency";
        this.textMillisecondsShort = "ms";
        // splash screen
        this.textAppDescription    = "Alarm Display for Fire Departments";
    }

}

export class LanguageDE extends Language {

    constructor() {
        super("de");

        this.months                = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "Novemeber", "Dezember"];
        this.weekdays              = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
        this.weekdaysShort         = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
        this.dateFormat            = "DD.MM.YYYY";
        this.dateFormatYearOnly    = "YYYY";
        this.timeFormatLong        = "HH:mm:ss";
        this.timeFormatShort       = "HH:mm";

        // invalid alarm
        this.textAlarm             = "Einsatz";
        // statistics
        this.textAlarmsTotal       = "Einsätze"; // "Gesamt";
        this.textAlarmsToday       = "Heute";
        // alarm history
        this.textAlarmHistory      = "Einsatzhistorie";
        this.textNoAlarmEntries    = "Bisher keine Einsätze";
        // calendar
        this.textCalendar          = "Terminplan";
        this.textNoCalendarEntries = "Keine bevorstehenden Termine";
        this.textNoCalendarError   = "Kein Kalender verfügbar";
        // status bar
        this.textConnected         = "Verbunden";
        this.textNotConnected      = "Nicht verbunden!";
        this.textReceptionOk       = "Empfang ok";
        this.textNoReception       = "Kein Empfang!";
        this.textLatency           = "Latenz";
        this.textMillisecondsShort = "ms";
        // splash screen
        this.textAppDescription    = "Alarmmonitor für Feuerwehr, THW und RD";
    }

}

export class LanguageEN extends Language {

    constructor() {
        super("en");

        //use default translation (en)
    }

}

export class LanguageENus extends Language {

    constructor() {
        super("en_us"); // super("en_ae");

        //use default translation (en)

        // adjust date format (AE)
        this.dateFormat            = "MM/DD/YYYY";
    }

}

export class LanguageENgb extends Language {

    constructor() {
        super("en_gb"); // super("en_be");

        //use default translation (en)

        // adjust date format (BE)
        this.dateFormat            = "DD/MM/YYYY";
    }

}
