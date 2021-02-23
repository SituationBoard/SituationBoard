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

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.util.StringConverter import StringConverter
from backend.api.WebSocket import WebSocket
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent

class ActionUpdateFrontend(Action):

    def __init__(self, instanceName: str, settings: Settings, webSocket: WebSocket):
        super().__init__("update_frontend", instanceName, settings)
        self.__webSocket = webSocket

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            alarmEvent = sourceEvent
            self.print(f"Sending alarm event #{alarmEvent.eventID}")
            self.__webSocket.broadcastAlarmEvent(alarmEvent)

        elif isinstance(sourceEvent, SettingEvent):
            settingEvent = sourceEvent
            settingName  = settingEvent.key.lower()
            settingValue = settingEvent.value
            settingValueSingleLine = StringConverter.string2singleline(settingValue)

            if settingName == "header":
                self.print("Sending setting " + settingName + " with value " + settingValueSingleLine)
                self.__webSocket.broadcastHeader(settingValue)
            elif settingName == "news":
                self.print("Sending setting " + settingName + " with value " + settingValueSingleLine)
                self.__webSocket.broadcastNews(settingValue)
            else:
                self.error(f"Invalid setting {settingName} (value: {settingValueSingleLine})")
