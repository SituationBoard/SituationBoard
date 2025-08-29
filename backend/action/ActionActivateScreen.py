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
        self.__maxAlarmAge = self.getSettingInt("max_alarm_age", 5 * 60) # in seconds; default = 5 minutes; 0 = handle always
        self.__handleAlarmUpdates = self.getSettingBoolean("handle_alarm_updates", True)

        self.__handleValid   = self.getSettingBoolean("handle_valid", True)
        self.__handleInvalid = self.getSettingBoolean("handle_invalid", True)
        self.__handleBinary  = self.getSettingBoolean("handle_binary", True)

        self.__cecDevice = self.getSettingString("cec_device", "") # use default if empty
        self.__screenDeviceID = self.getSettingInt("screen_device_id", 0) # TV should always be 0
        self.__timeout = self.getSettingInt("timeout", 10) # 10 seconds

        if self.isDebug():
            self.dbgPrint("List of CEC Devices:")
            self.dbgPrint(self.__displayPowerManager.listCECDevices())
            self.dbgPrint(f"Device Scan (for cec_device=\"{self.__cecDevice}\"):")
            self.dbgPrint(self.__displayPowerManager.scanDevices(self.__cecDevice))

        self.__activationTimestamp = 0.0

        self.__displayDevice = self.__displayPowerManager.getDevice(self.__cecDevice, self.__screenDeviceID, self.__timeout)
        if self.__displayDevice.getPowerState() is None:
            self.error(f"Failed to connect to the screen (cec_device=\"{self.__cecDevice}\", screen_device_id={self.__screenDeviceID})")

    def __activateScreen(self) -> None:
        isActive = self.__displayDevice.getPowerState()
        if isActive is None:
            self.error("Failed to retrieve power state of the screen")
        elif isActive:
            if self.__activeDuration != 0 and self.__activationTimestamp != 0:
                self.dbgPrint("Screen was already active (prior event)")
                self.__activationTimestamp = time.time() # -> update timestamp to delay deactivation
            else:
                self.dbgPrint("Screen was already active (manual)")
            return

        success = self.__displayDevice.powerOn()
        if not success:
            self.error("Failed to activate screen")
            return

        if self.__activeDuration != 0:
            self.__activationTimestamp = time.time()

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            if sourceEvent.updated and not self.__handleAlarmUpdates:
                self.dbgPrint("Ignored alarm event (update)")
                return

            if sourceEvent.isOutdated(self.__maxAlarmAge):
                self.dbgPrint("Ignored alarm event (outdated)")
                return

            if sourceEvent.valid:
                if not self.__handleValid:
                    self.dbgPrint("Ignored alarm event (valid)")
                    return
            elif sourceEvent.invalid:
                if not self.__handleInvalid:
                    self.dbgPrint("Ignored alarm event (invalid)")
                    return
            elif sourceEvent.binary:
                if not self.__handleBinary:
                    self.dbgPrint("Ignored alarm event (binary)")
                    return
            else:
                return

            self.print("Activate screen (alarm event)")
            self.__activateScreen()
        elif isinstance(sourceEvent, SettingEvent):
            self.print("Activate screen (setting event)")
            self.__activateScreen()

    def handleCyclic(self) -> None:
        if self.__activationTimestamp != 0:
            nowTimestamp = time.time()
            endTimestamp = self.__activationTimestamp + self.__activeDuration
            if nowTimestamp >= endTimestamp:
                self.__activationTimestamp = 0
                self.print("Deactivate screen")
                self.__displayDevice.powerOff()
