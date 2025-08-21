# SituationBoard - Alarm Display for Fire Departments
# Copyright (C) 2017-2021 Sebastian Maier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import signal
import types

from typing import Optional
from threading import Thread
from http import HTTPStatus

from flask import Flask, Response, request, abort

from backend.util.SignalLock import SignalLock

class DiveraMockAPI:

    ALARM_NONE = """{"success": false, "cached": false}"""

    ALARM_0 = """{"success": true, "cached": true, "data": {"id": 10000, "author_id": 20000, "cluster_id": 30000, "alarmcode_id": 0, "message_channel_id": 0, "foreign_id": "40000", "title": "B BMA #B1710#Meldeanlage#Brandmeldeanlage", "text": "Lager, BMA hat ausgel\u00f6st", "report": "", "address": "Hauptstra\u00dfe 112  12345 Musterdorf", "lat": 49.0, "lng": 11.0, "priority": true, "date": 1754803909, "new": false, "editable": false, "answerable": false, "notification_type": 2, "vehicle": [1120, 1121], "group": [], "cluster": [], "user_cluster_relation": [], "hidden": false, "deleted": false, "message_channel": false, "custom_answers": false, "attachment_count": 0, "closed": false, "close_state": -1, "duration": "", "ts_response": 1754807509, "response_time": 3600, "ucr_addressed": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527], "ucr_answered": {"99148": {"500": {"ts": 1754805534, "note": ""}, "501": {"ts": 1754804021, "note": ""}, "502": {"ts": 1754803993, "note": ""}, "503": {"ts": 1754803958, "note": ""}, "504": {"ts": 1754803934, "note": ""}}, "99150": {"505": {"ts": 1754805200, "note": ""}, "506": {"ts": 1754804204, "note": ""}, "507": {"ts": 1754803961, "note": ""}, "508": {"ts": 1754803945, "note": ""}, "509": {"ts": 1754803929, "note": ""}, "510": {"ts": 1754803919, "note": ""}, "511": {"ts": 1754803919, "note": ""}}}, "ucr_answeredcount": {"99148": 5, "99150": 7}, "ucr_read": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513], "ucr_self_addressed": false, "count_recipients": 28, "count_read": 14, "private_mode": false, "custom": [], "ts_publish": 0, "ts_create": 1754803909, "ts_update": 1754805534, "ts_close": 0, "notification_filter_vehicle": false, "notification_filter_status": false, "notification_filter_shift_plan": 0, "notification_filter_access": false, "notification_filter_status_access": false, "ucr_self_status_id": 0, "ucr_self_note": ""}}"""

    ALARM_0_UPDATED = """{"success": true, "cached": true, "data": {"id": 10000, "author_id": 20000, "cluster_id": 30000, "alarmcode_id": 0, "message_channel_id": 0, "foreign_id": "40000", "title": "B BMA #B1710#Meldeanlage#Brandmeldeanlage", "text": "Lager, BMA hat ausgel\u00f6st", "report": "", "address": "Hauptstra\u00dfe 112  12345 Musterdorf", "lat": 49.0, "lng": 11.0, "priority": true, "date": 1754803909, "new": false, "editable": false, "answerable": false, "notification_type": 2, "vehicle": [1120, 1121], "group": [], "cluster": [], "user_cluster_relation": [], "hidden": false, "deleted": false, "message_channel": false, "custom_answers": false, "attachment_count": 0, "closed": false, "close_state": -1, "duration": "", "ts_response": 1754807509, "response_time": 3600, "ucr_addressed": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527], "ucr_answered": {"99148": {"500": {"ts": 1754805534, "note": ""}, "501": {"ts": 1754804021, "note": ""}, "502": {"ts": 1754803993, "note": ""}, "503": {"ts": 1754803958, "note": ""}, "504": {"ts": 1754803934, "note": ""}}, "99150": {"505": {"ts": 1754805200, "note": ""}, "506": {"ts": 1754804204, "note": ""}, "507": {"ts": 1754803961, "note": ""}, "508": {"ts": 1754803945, "note": ""}, "509": {"ts": 1754803929, "note": ""}, "510": {"ts": 1754803919, "note": ""}, "511": {"ts": 1754803919, "note": ""}}}, "ucr_answeredcount": {"99148": 5, "99150": 7}, "ucr_read": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515], "ucr_self_addressed": false, "count_recipients": 28, "count_read": 16, "private_mode": false, "custom": [], "ts_publish": 0, "ts_create": 1754803909, "ts_update": 1754808618, "ts_close": 0, "notification_filter_vehicle": false, "notification_filter_status": false, "notification_filter_shift_plan": 0, "notification_filter_access": false, "notification_filter_status_access": false, "ucr_self_status_id": 0, "ucr_self_note": ""}}"""

    ALARM_1 = """{"success": true, "cached": true, "data": {"id": 10001, "author_id": 0, "cluster_id": 30000, "alarmcode_id": 0, "message_channel_id": 0, "foreign_id": "", "title": "Probealarm", "text": "Probealarm \u00fcber DIVERA", "report": "", "address": "Hauptstra\u00dfe 112, 12345 Musterdorf", "lat": 0, "lng": 0, "priority": true, "date": 1754731818, "new": false, "editable": false, "answerable": false, "notification_type": 3, "vehicle": [], "group": [40000], "cluster": [], "user_cluster_relation": [], "hidden": false, "deleted": false, "message_channel": false, "custom_answers": false, "attachment_count": 0, "closed": false, "close_state": -1, "duration": "", "ts_response": 0, "response_time": 0, "ucr_addressed": [500], "ucr_answered": {"99150": {"500": {"ts": 1754731844, "note": ""}}}, "ucr_answeredcount": {"99150": 1}, "ucr_read": [500], "ucr_self_addressed": false, "count_recipients": 1, "count_read": 1, "private_mode": false, "custom": [], "ts_publish": 0, "ts_create": 1754731818, "ts_update": 1754731852, "ts_close": 0, "notification_filter_vehicle": false, "notification_filter_status": false, "notification_filter_shift_plan": 0, "notification_filter_access": false, "notification_filter_status_access": false, "ucr_self_status_id": 0, "ucr_self_note": ""}}"""

    VEHICLE_STATUS_NONE =  """{"success": false, "cached": false}"""

    VEHICLE_STATUS_0 = """{"success": true, "data": [{"id": 0, "fullname": "L\u00f6schgruppenfahrzeug", "shortname": "LF", "name": "43/1", "fmsstatus": 2, "fmsstatus_id": 2, "fmsstatus_note": "", "fmsstatus_ts": 1754806190, "crew": [], "lat": 0, "lng": 0, "opta": "", "issi": "", "number": "MD-FW-112"}, {"id": 1, "fullname": "Mannschaftstransporter", "shortname": "MTW", "name": "14/1", "fmsstatus": 2, "fmsstatus_id": 2, "fmsstatus_note": "", "fmsstatus_ts": 1754805883, "crew": [], "lat": 0, "lng": 0, "opta": "", "issi": "", "number": "MD-FW-113"}]}"""

    VEHICLE_STATUS_1 = """{"success": true, "data": [{"id": 1120, "fullname": "L\u00f6schgruppenfahrzeug", "shortname": "LF", "name": "43/1", "fmsstatus": 1, "fmsstatus_id": 1, "fmsstatus_note": "", "fmsstatus_ts": 1754806190, "crew": [], "lat": 0, "lng": 0, "opta": "", "issi": "", "number": "MD-FW-112"}, {"id": 1121, "fullname": "Mannschaftstransporter", "shortname": "MTW", "name": "14/1", "fmsstatus": 1, "fmsstatus_id": 1, "fmsstatus_note": "", "fmsstatus_ts": 1754805883, "crew": [], "lat": 0, "lng": 0, "opta": "", "issi": "", "number": "MD-FW-113"}]}"""

    KEY_VALID   = "ABC12345"
    KEY_INVALID = "ABC00000"

    DEFAULT_API_HOST = "localhost"
    DEFAULT_API_PORT = 12345
    DEFAULT_API_KEY  = KEY_VALID

    def __init__(self, accessKey: str = DEFAULT_API_KEY) -> None:
        self.app = Flask(__name__)
        self.app.testing = True

        self.app.add_url_rule("/api/last-alarm",             'last-alarm',     self.__get_last_alarm,     methods=["GET"])
        self.app.add_url_rule("/api/v2/pull/vehicle-status", 'vehicle-status', self.__get_vehicle_status, methods=["GET"])

        signals = [signal.SIGALRM, signal.SIGUSR1, signal.SIGUSR2]
        self.signalLock = SignalLock(signals)

        # initial state
        self.expectedAccessKey: str = accessKey
        self.httpStatusOverride: Optional[HTTPStatus] = None
        self.currentAlarm: str = DiveraMockAPI.ALARM_NONE
        self.currentVehicleStatus: str = DiveraMockAPI.VEHICLE_STATUS_0

        # interactive mode
        self.alarmList = [DiveraMockAPI.ALARM_0, DiveraMockAPI.ALARM_0_UPDATED, DiveraMockAPI.ALARM_1]
        self.vehicleStatusList = [DiveraMockAPI.VEHICLE_STATUS_1, DiveraMockAPI.VEHICLE_STATUS_0]
        self.httpStatusList = [HTTPStatus.FORBIDDEN, None]
        self.nextAlarmIndex = 0
        self.nextVehicleStatusIndex = 0
        self.nextHTTPStatusIndex = 0

    def __signal_handler(self, signum: int, frame: Optional[types.FrameType]) -> None: #pylint: disable=no-member
        if signum == signal.SIGALRM:
            alarm = self.alarmList[self.nextAlarmIndex]
            self.nextAlarmIndex = (self.nextAlarmIndex + 1) % len(self.alarmList)
            self.set_current_alarm(alarm)
        elif signum == signal.SIGUSR1:
            httpStatus = self.httpStatusList[self.nextHTTPStatusIndex]
            self.nextHTTPStatusIndex = (self.nextHTTPStatusIndex + 1) % len(self.httpStatusList)
            self.set_http_status_override(httpStatus)
        elif signum == signal.SIGUSR2:
            vehicleStatus = self.vehicleStatusList[self.nextVehicleStatusIndex]
            self.nextVehicleStatusIndex = (self.nextVehicleStatusIndex + 1) % len(self.vehicleStatusList)
            self.set_current_vehicle_status(vehicleStatus)

    def __thread_function(self, host: str, port: int) -> None:
        self.app.run(host, port)

    def run(self, host: str = DEFAULT_API_HOST, port: int = DEFAULT_API_PORT, interactive: bool = True) -> None:
        if interactive:
            # register signal handler
            signal.signal(signal.SIGALRM, self.__signal_handler) # SIGALRM triggers an alarm (or an alarm update)
            signal.signal(signal.SIGUSR1, self.__signal_handler) # SIGUSR1 toggles between succeeding and failing API calls
            signal.signal(signal.SIGUSR2, self.__signal_handler) # SIGUSR2 triggers an update of vehicle status

        apiThread = Thread(target=self.__thread_function, args=(host, port), daemon=True)
        apiThread.start()
        time.sleep(1)

    def set_access_key(self, key: str) -> None:
        with self.signalLock:
            self.expectedAccessKey = key

    def set_http_status_override(self, status: Optional[HTTPStatus]) -> None:
        with self.signalLock:
            self.httpStatusOverride = status

    def set_current_alarm(self, alarm: str) -> None:
        with self.signalLock:
            self.currentAlarm = alarm

    def set_current_vehicle_status(self, status: str) -> None:
        with self.signalLock:
            self.currentVehicleStatus = status

    def __handle_request(self, data: str) -> Response:
        if self.httpStatusOverride is not None:
            abort(self.httpStatusOverride)

        accesskey = request.args.get("accesskey", "")
        if accesskey != self.expectedAccessKey:
            abort(HTTPStatus.FORBIDDEN)

        response = Response(data, HTTPStatus.OK, mimetype='application/json')
        return response

    def __get_last_alarm(self) -> Response:
        with self.signalLock:
            return self.__handle_request(self.currentAlarm)

    def __get_vehicle_status(self) -> Response:
        with self.signalLock:
            return self.__handle_request(self.currentVehicleStatus)
