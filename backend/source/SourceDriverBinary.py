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

import datetime
from typing import Optional

import RPi.GPIO as GPIO #pylint: disable=import-error

from backend.source.SourceDriver import SourceDriver, SourceState
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.util.Settings import Settings

class SourceDriverBinary(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__("binary", instanceName, settings, multipleInstances=True)
        self.__alarmMessage = self.getSettingString("message", "Alarm")
        self.__pin = self.getSettingInt("pin", 13) # BCM
        self.__active_high = self.getSettingBoolean("active_high", False)

        self.__alarmTime: Optional[datetime.datetime] = None

        GPIO.setmode(GPIO.BCM)
        if self.__active_high:
            self.dbgPrint(f"active high for pin {self.__pin}")
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(self.__pin, GPIO.RISING, callback=self.alarmCallback, bouncetime=1000)
        else:
            self.dbgPrint(f"active low for pin {self.__pin}")
            GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.__pin, GPIO.FALLING, callback=self.alarmCallback, bouncetime=1000)

    def alarmCallback(self, channel: int) -> None:
        self.__alarmTime = datetime.datetime.now()

    def retrieveEvent(self) -> Optional[SourceEvent]:
        alarmEvent = None

        if self.__alarmTime is not None:
            # ensure signal is still active (prevent noise from triggering an alarm)
            if GPIO.input(self.__pin) != self.__active_high:
                self.__alarmTime = None
            else:
                self.clrPrint("Detected binary alarm")

                ts = self.__alarmTime.strftime(AlarmEvent.TIMESTAMP_FORMAT)

                alarmEvent = AlarmEvent()
                alarmEvent.timestamp      = ts
                alarmEvent.alarmTimestamp = ts
                alarmEvent.source         = AlarmEvent.SOURCE_BINARY
                alarmEvent.flags          = AlarmEvent.FLAGS_BINARY
                alarmEvent.raw            = self.__alarmMessage

                self.__alarmTime = None

        return alarmEvent

    def getSourceState(self) -> SourceState:
        return SourceState.OK
