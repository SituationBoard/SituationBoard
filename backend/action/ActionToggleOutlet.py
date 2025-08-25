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

import json
import time

import http.client as HTTPClient

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent

class ActionToggleOutlet(Action):

    API_SET = "/relay?state={STATE}" # STATE=0 (OFF) STATE=1 (ON)
    API_TOGGLE = "/toggle"
    API_REPORT = "/report"

    def __init__(self, instanceName: str, settings: Settings):
        super().__init__("toggle_outlet", instanceName, settings, multipleInstances=True)
        self.__apiURL = self.getSettingString("api_url", "")
        self.__timeout = self.getSettingInt("timeout", 2)
        self.__inverted = self.getSettingBoolean("inverted", False)
        self.__resetOnStartup = self.getSettingBoolean("reset_on_startup", True)
        self.__activeDuration = self.getSettingInt("active_duration", 15 * 60) # in seconds; 0 = forever
        self.__maxAlarmAge = self.getSettingInt("max_alarm_age", 5 * 60) # in seconds; default = 5 minutes; 0 = handle always
        self.__handleAlarmUpdates = self.getSettingBoolean("handle_alarm_updates", False)

        self.__toggleValid   = self.getSettingBoolean("toggle_valid", True)
        self.__toggleInvalid = self.getSettingBoolean("toggle_invalid", True)
        self.__toggleBinary  = self.getSettingBoolean("toggle_binary", True)

        self.__activationTimestamp = 0.0

        if self.__apiURL == "":
            self.fatal("No API URL specified in configuration")

        if self.__resetOnStartup:
            self.deactivateOutlet()

    def setState(self, state: int) -> bool:
        completeRequest = ActionToggleOutlet.API_SET.format(STATE = state)

        self.dbgPrint(self.__apiURL + completeRequest)

        try:
            self.dbgPrint(f"Sending API request to outlet {self.__apiURL} (new state: {state})")

            connection = HTTPClient.HTTPConnection(self.__apiURL, 80, timeout=self.__timeout)
            connection.connect()

            self.dbgPrint(f"API request:\n{completeRequest}")

            connection.request('GET', completeRequest)
            response = connection.getresponse().read().decode("utf-8")
            try:
                result = json.loads(response)
                self.dbgPrint(f"API response:\n{json.dumps(result)}")
            except Exception:
                self.dbgPrint(f"API response:\n{response}")

            return True

        except Exception as e:
            self.error(f"Failed to toggle outlet {self.__apiURL} ({e})")

            return False

    def activateOutlet(self) -> None:
        if self.__inverted:
            self.print(f"Turning outlet {self.__apiURL} off")
            self.setState(0)
        else:
            self.print(f"Turning outlet {self.__apiURL} on")
            self.setState(1)

    def deactivateOutlet(self) -> None:
        if self.__inverted:
            self.print(f"Turning outlet {self.__apiURL} on")
            self.setState(1)
        else:
            self.print(f"Turning outlet {self.__apiURL} off")
            self.setState(0)

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

            self.activateOutlet()

    def handleCyclic(self) -> None:
        if self.__activationTimestamp != 0:
            nowTimestamp = time.time()
            endTimestamp = self.__activationTimestamp + self.__activeDuration
            if nowTimestamp >= endTimestamp:
                self.__activationTimestamp = 0
                self.deactivateOutlet()
