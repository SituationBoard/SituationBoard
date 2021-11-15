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

import signal
import datetime
import types
# import os

from typing import Optional

from backend.source.SourceDriver import SourceDriver, SourceState
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.util.Settings import Settings

class SourceDriverDummy(SourceDriver):

    MAX_ALARMS    = 3
    MAX_SETTINGS  = 4

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__("dummy", instanceName, settings)
        self.__triggerBinary   = False
        self.__triggerAlarm    = False
        self.__triggerSetting  = False
        self.__nextAlarm       = 0
        self.__nextSetting     = 0

        # self.print(f"PID = {os.getpid()}")

        # Register signal handlers
        signal.signal(signal.SIGALRM, self.__signalHandler) # SIGALRM triggers a text alarm message
        signal.signal(signal.SIGUSR1, self.__signalHandler) # SIGUSR1 triggers a binary alarm message
        signal.signal(signal.SIGUSR2, self.__signalHandler) # SIGUSR2 triggers a setting message

    def retrieveEvent(self) -> Optional[SourceEvent]:
        if self.__triggerBinary:
            self.__triggerBinary = False
            self.clrPrint("Generating new dummy binary alarm")
            return self.__generateBinaryEvent()

        if self.__triggerAlarm:
            self.__triggerAlarm = False
            self.clrPrint("Generating new dummy alarm message")
            return self.__generateAlarmEvent()

        if self.__triggerSetting:
            self.__triggerSetting = False
            self.clrPrint("Generating new dummy setting message")
            return self.__generateSettingEvent()

        return None

    def getSourceState(self) -> SourceState:
        return SourceState.OK # Dummy connection is always ok

    def __signalHandler(self, signum: int, frame: Optional[types.FrameType]) -> None: #pylint: disable=no-member
        if signum == signal.SIGALRM:
            self.__triggerAlarm = True
        elif signum == signal.SIGUSR1:
            self.__triggerBinary = True
        elif signum == signal.SIGUSR2:
            self.__triggerSetting = True

    def __generateBinaryEvent(self) -> AlarmEvent:
        binaryEvent = AlarmEvent()

        moment = datetime.datetime.now()
        ts = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)
        binaryEvent.timestamp      = ts
        binaryEvent.alarmTimestamp = ts
        binaryEvent.source         = AlarmEvent.SOURCE_DUMMY
        binaryEvent.flags          = AlarmEvent.FLAGS_BINARY
        binaryEvent.raw            = "Einsatzalarmierung"

        return binaryEvent

    def __generateAlarmEvent(self) -> AlarmEvent:
        alarmEvent = AlarmEvent()

        moment = datetime.datetime.now()
        ts = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)

        alarmEvent.timestamp      = ts
        alarmEvent.alarmTimestamp = ts
        alarmEvent.source         = AlarmEvent.SOURCE_DUMMY
        alarmEvent.flags          = AlarmEvent.FLAGS_VALID
        alarmEvent.raw            = "Dummy Alarm Message"
        alarmEvent.sender         = "112"

        if self.__nextAlarm == 0:
            alarmEvent.event           = "T 1"
            alarmEvent.eventDetails    = "Test 1"
            alarmEvent.location        = "Musterdorf"
            alarmEvent.locationDetails = "Hauptstraße 112"
            alarmEvent.comment         = "Nix los hier"
        elif self.__nextAlarm == 1:
            alarmEvent.event           = "T 2"
            alarmEvent.eventDetails    = "Test 2"
            alarmEvent.location        = "Musterheim"
            alarmEvent.locationDetails = "Hauptstraße 112"
            alarmEvent.comment         = "Nix los hier"
        elif self.__nextAlarm == 2:
            alarmEvent.event           = "T 3"
            alarmEvent.eventDetails    = "Test 3"
            alarmEvent.location        = "Musterstadt"
            alarmEvent.locationDetails = "Hauptstraße 112"
            alarmEvent.comment         = "Nix los hier"

        # dummy location for maps
        #alarmEvent.location          = "<SPECIFY CITY>"
        #alarmEvent.locationDetails   = "<SPECIFY STREET>"

        # dummy comment to test CSV import/export
        #alarmEvent.comment           = "Test \"Test\" \\n Test;Test\nTest Test"

        # dummy alarm for screenshots
        #alarmEvent.event             = "B 1"
        #alarmEvent.eventDetails      = "Brand - Freifläche klein"
        #alarmEvent.location          = "Musterdorf"
        #alarmEvent.locationDetails   = "Hauptstraße 112"
        #alarmEvent.comment           = "Acker/Freifläche nahe Schloss\nBrennende Fläche < 100 qm"
        #alarmEvent.locationLatitude  = 0.0 # specify random location here for screenshots of the map
        #alarmEvent.locationLongitude = 0.0 # specify random location here for screenshots of the map

        self.__nextAlarm = (self.__nextAlarm + 1) % SourceDriverDummy.MAX_ALARMS

        return alarmEvent

    def __generateSettingEvent(self) -> SettingEvent:
        settingEvent = SettingEvent()

        moment = datetime.datetime.now()
        settingEvent.timestamp = moment.strftime(SettingEvent.TIMESTAMP_FORMAT)
        settingEvent.source    = SettingEvent.SOURCE_DUMMY
        settingEvent.flags     = SettingEvent.FLAGS_VALID
        settingEvent.raw       = "Settings Message"
        settingEvent.sender    = "12345"

        if self.__nextSetting == 0:
            settingEvent.key   = "header"
            settingEvent.value = "Feuerwehr Musterdorf"
        elif self.__nextSetting == 1:
            settingEvent.key   = "news"
            settingEvent.value = "Herzlich Willkommen"
        elif self.__nextSetting == 2:
            settingEvent.key   = "news"
            settingEvent.value = ""
        elif self.__nextSetting == 3:
            settingEvent.key   = "header"
            settingEvent.value = ""

        self.__nextSetting = (self.__nextSetting + 1) % SourceDriverDummy.MAX_SETTINGS

        return settingEvent
