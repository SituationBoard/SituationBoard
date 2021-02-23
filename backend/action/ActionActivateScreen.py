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

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent

class ActionActivateScreen(Action):

    def __init__(self, instanceName: str, settings: Settings, displayPowerManager: DisplayPowerManager):
        super().__init__("activate_screen", instanceName, settings)
        self.__displayPowerManager = displayPowerManager
        self.__activeDuration = self.getSettingInt("active_duration", 0) # in seconds; 0 = forever
        self.__activationTimestamp = 0.0

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            if self.__activeDuration != 0:
                self.__activationTimestamp = time.time()

            self.print("Activate screen (alarm event)")
            self.__displayPowerManager.powerOn()

        elif isinstance(sourceEvent, SettingEvent):
            if self.__activeDuration != 0:
                self.__activationTimestamp = time.time()

            self.print("Activate screen (setting event)")
            self.__displayPowerManager.powerOn()

    def handleCyclic(self) -> None:
        if self.__activationTimestamp != 0:
            nowTimestamp = time.time()
            endTimestamp = self.__activationTimestamp + self.__activeDuration
            if nowTimestamp >= endTimestamp:
                self.__activationTimestamp = 0
                self.print("Deactivate screen")
                self.__displayPowerManager.powerOff()
