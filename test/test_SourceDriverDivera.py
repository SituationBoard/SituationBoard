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

import os
import time
import shutil
import datetime

from typing import Any

from test.DiveraMockAPI import DiveraMockAPI

from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.util.Plugin import Plugin
from backend.source.SourceDriver import SourceState
from backend.source.SourceDriverDivera import SourceDriverDivera

from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent

class Test_SourceDriverDivera:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        self.urlRegular = f"http://{DiveraMockAPI.DEFAULT_API_HOST}:{DiveraMockAPI.DEFAULT_API_PORT}"
        self.urlNotAvailable = "http://na:12345"

        s = Settings(settingsFilename, appInfo.path)

        section = SourceDriverDivera.PLUGIN_TYPE + Plugin.NAME_SEPARATOR + "divera"
        s.setBoolean(section, "debug", True)
        s.setString(section, "api_key", DiveraMockAPI.DEFAULT_API_KEY) # use the API key from our mock API
        s.setInt(section, "timeout", 5) # 5 seconds
        s.setString(section, "api_url", self.urlRegular) # use mocked REST API
        s.setBoolean(section, "ignore_test_alarm", False)
        s.setBoolean(section, "show_vehicle_status", True)
        s.setBoolean(section, "show_crew_responses", True)
        s.setString(section, "response_id_fast", "99148")
        s.setString(section, "response_id_slow", "99149")
        s.setString(section, "response_id_na", "99150")
        s.setBoolean(section, "use_mock_api", False) # we provide our own instance of the mock API for testing

        self.a = DiveraMockAPI(DiveraMockAPI.DEFAULT_API_KEY)
        self.a.run(DiveraMockAPI.DEFAULT_API_HOST, DiveraMockAPI.DEFAULT_API_PORT, interactive=False)

        self.d = SourceDriverDivera("", s, None, self.a)

    def __checkAlarmTimestamp(self, e: Any, timestampExpected: str) -> None:
        assert(isinstance(e, AlarmEvent))

        timestampActual = e.alarmTimestamp
        aParsed = datetime.datetime.strptime(timestampActual, AlarmEvent.TIMESTAMP_FORMAT)
        aTS = aParsed.timestamp()
        timezone = datetime.timezone(datetime.timedelta(hours=+2))
        adjusted = datetime.datetime.fromtimestamp(aTS, tz=timezone)

        assert(datetime.datetime.strftime(adjusted, AlarmEvent.TIMESTAMP_FORMAT) == timestampExpected)

    def __checkAlarmEventCommon(self, e: Any, raw: str) -> None:
        assert(isinstance(e, AlarmEvent))

        assert(e.timestamp != "")
        assert(e.source == SourceEvent.SOURCE_DIVERA)
        assert(e.sender == self.urlRegular)
        assert(e.flags == AlarmEvent.FLAGS_VALID)
        assert(e.raw == raw)

    def __checkAlarmEvent0(self, e: Any, updated: bool = False, eOrig: Any = None) -> None:
        if updated:
            self.__checkAlarmEventCommon(e, DiveraMockAPI.ALARM_0_UPDATED)
            assert(e is eOrig)
            assert(e.eventID != AlarmEvent.NO_ID)
            assert(e.comment == "Lager, BMA hat ausgelöst\n\nPRIO 16/28 >> fast: 5 – slow: 0 – n/a: 7")
        else:
            self.__checkAlarmEventCommon(e, DiveraMockAPI.ALARM_0)
            assert(e.eventID == AlarmEvent.NO_ID)
            assert(e.comment == "Lager, BMA hat ausgelöst\n\nPRIO 14/28 >> fast: 5 – slow: 0 – n/a: 7")

        assert(e.event == "B BMA")
        assert(e.eventDetails == "#B1710#Meldeanlage#Brandmeldeanlage")
        assert(e.location == "12345 Musterdorf")
        assert(e.locationDetails == "Hauptstraße 112")
        assert(e.locationLatitude == 49.0)
        assert(e.locationLongitude == 11.0)
        self.__checkAlarmTimestamp(e, "2025-08-10 07:31:49")

    def __checkAlarmEvent1(self, e: Any) -> None:
        self.__checkAlarmEventCommon(e, DiveraMockAPI.ALARM_1)

        assert(e.eventID == AlarmEvent.NO_ID)
        assert(e.event == "Probealarm")
        assert(e.eventDetails == "")
        assert(e.location == "12345 Musterdorf")
        assert(e.locationDetails == "Hauptstraße 112")
        assert(e.locationLatitude == 0)
        assert(e.locationLongitude == 0)
        assert(e.comment == "Probealarm über DIVERA\n\nPRIO 1/1 >> fast: 0 – slow: 0 – n/a: 1")
        self.__checkAlarmTimestamp(e, "2025-08-09 11:30:18")

    def __checkVehicleStatusCommon(self, e: Any, raw: str, sender: str) -> None:
        assert(isinstance(e, SettingEvent))

        assert(e.timestamp != "")
        assert(e.source == SourceEvent.SOURCE_DIVERA)
        assert(e.sender == sender)
        assert(e.flags == SettingEvent.FLAGS_VALID)
        assert(e.raw == raw)

        assert(e.key == "news")

    def __checkVehicleStatusNone(self, e: Any, raw: str, sender: str) -> None:
        self.__checkVehicleStatusCommon(e, raw, sender)

        assert(e.value == "")

    def __checkVehicleStatus0(self, e: Any) -> None:
        self.__checkVehicleStatusCommon(e, DiveraMockAPI.VEHICLE_STATUS_0, self.urlRegular)

        assert(e.value == "LF 43/1: Status 2  –  MTW 14/1: Status 2")

    def __checkVehicleStatus1(self, e: Any) -> None:
        self.__checkVehicleStatusCommon(e, DiveraMockAPI.VEHICLE_STATUS_1, self.urlRegular)

        assert(e.value == "LF 43/1: Status 1  –  MTW 14/1: Status 1")

    def test_source_state(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_NONE)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        state = self.d.getSourceState()
        assert(state == SourceState.ERROR)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        self.a.set_access_key(DiveraMockAPI.KEY_INVALID)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatusNone(e, "", self.urlRegular)

        state = self.d.getSourceState()
        assert(state == SourceState.ERROR)

        e = self.d.retrieveEvent()
        assert(e is None)

        state = self.d.getSourceState()
        assert(state == SourceState.ERROR)

    def test_vehicle_status(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_NONE)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        e = self.d.retrieveEvent()
        assert(e is None)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_1)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus1(e)

        e = self.d.retrieveEvent()
        assert(e is None)

        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_NONE)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatusNone(e, DiveraMockAPI.VEHICLE_STATUS_NONE, self.urlRegular)

        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_1)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus1(e)

        self.a.set_access_key(DiveraMockAPI.KEY_INVALID)
        time.sleep(1.2)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatusNone(e, "", self.urlRegular)

    def test_alarmNone(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_NONE)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        e = self.d.retrieveEvent()
        assert(e is None)

    def test_alarm0(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_NONE)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        self.a.set_current_alarm(DiveraMockAPI.ALARM_0)

        eOrig = self.d.retrieveEvent()
        self.__checkAlarmEvent0(eOrig)

        assert(isinstance(eOrig, AlarmEvent))
        aeOrig = eOrig
        aeOrig.eventID = 1234

        e = self.d.retrieveEvent()
        assert(e is None)

        self.a.set_current_alarm(DiveraMockAPI.ALARM_0_UPDATED)

        eNext = self.d.retrieveEvent()
        self.__checkAlarmEvent0(eNext, True, eOrig)

        e = self.d.retrieveEvent()
        assert(e is None)


    def test_alarm1(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_1)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        e = self.d.retrieveEvent()
        self.__checkAlarmEvent1(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        e = self.d.retrieveEvent()
        assert(e is None)

    def test_url_na(self) -> None:
        self.d.testResetSourceState()

        self.a.set_access_key(DiveraMockAPI.KEY_VALID)
        self.a.set_current_alarm(DiveraMockAPI.ALARM_0)
        self.a.set_current_vehicle_status(DiveraMockAPI.VEHICLE_STATUS_0)

        e = self.d.retrieveEvent()
        self.__checkAlarmEvent0(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        self.d.testSetAPIURL(self.urlNotAvailable)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatusNone(e, "", self.urlNotAvailable)

        state = self.d.getSourceState()
        assert(state == SourceState.ERROR)

        e = self.d.retrieveEvent()
        assert(e is None)

        state = self.d.getSourceState()
        assert(state == SourceState.ERROR)

        self.d.testSetAPIURL(self.urlRegular)

        e = self.d.retrieveEvent()
        self.__checkVehicleStatus0(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        self.a.set_current_alarm(DiveraMockAPI.ALARM_1)

        e = self.d.retrieveEvent()
        self.__checkAlarmEvent1(e)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)

        e = self.d.retrieveEvent()
        assert(e is None)

        state = self.d.getSourceState()
        assert(state == SourceState.OK)
