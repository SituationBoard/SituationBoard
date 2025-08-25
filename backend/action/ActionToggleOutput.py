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

from RPi import GPIO #pylint: disable=import-error

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent

class ActionToggleOutput(Action):

    def __init__(self, instanceName: str, settings: Settings):
        super().__init__("toggle_output", instanceName, settings, multipleInstances=True)
        self.__pin = self.getSettingInt("pin", 0) # BCM
        self.__active_high = self.getSettingBoolean("active_high", True)
        self.__resetOnStartup = self.getSettingBoolean("reset_on_startup", True)
        self.__activeDuration = self.getSettingInt("active_duration", 15 * 60) # in seconds; 0 = forever
        self.__maxAlarmAge = self.getSettingInt("max_alarm_age", 5 * 60) # in seconds; default = 5 minutes; 0 = handle always
        self.__handleAlarmUpdates = self.getSettingBoolean("handle_alarm_updates", False)

        self.__toggleValid   = self.getSettingBoolean("toggle_valid", True)
        self.__toggleInvalid = self.getSettingBoolean("toggle_invalid", True)
        self.__toggleBinary  = self.getSettingBoolean("toggle_binary", True)

        self.__activationTimestamp = 0.0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin, GPIO.OUT)

        if self.__resetOnStartup:
            self.deactivatePin()

    def activatePin(self) -> None:
        if self.__active_high:
            self.print(f"Setting IO pin {self.__pin} to high")
            GPIO.output(self.__pin, GPIO.HIGH)
        else:
            self.print(f"Setting IO pin {self.__pin} to low")
            GPIO.output(self.__pin, GPIO.LOW)

    def deactivatePin(self) -> None:
        if self.__active_high:
            self.print(f"Setting IO pin {self.__pin} to low")
            GPIO.output(self.__pin, GPIO.LOW)
        else:
            self.print(f"Setting IO pin {self.__pin} to high")
            GPIO.output(self.__pin, GPIO.HIGH)

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            alarmEvent = sourceEvent

            if alarmEvent.valid:
                if not self.__toggleValid:
                    self.dbgPrint("Ignored alarm event (valid)")
                    return
            elif alarmEvent.invalid:
                if not self.__toggleInvalid:
                    self.dbgPrint("Ignored alarm event (invalid)")
                    return
            elif alarmEvent.binary:
                if not self.__toggleBinary:
                    self.dbgPrint("Ignored alarm event (binary)")
                    return
            else:
                return

            if alarmEvent.updated and not self.__handleAlarmUpdates:
                self.dbgPrint("Ignored alarm event (update)")
                return

            if alarmEvent.isOutdated(self.__maxAlarmAge):
                self.dbgPrint("Ignored alarm event (outdated)")
                return

            if self.__activeDuration != 0:
                self.__activationTimestamp = time.time()

            self.activatePin()

    def handleCyclic(self) -> None:
        if self.__activationTimestamp != 0:
            nowTimestamp = time.time()
            endTimestamp = self.__activationTimestamp + self.__activeDuration
            if nowTimestamp >= endTimestamp:
                self.__activationTimestamp = 0
                self.deactivatePin()
