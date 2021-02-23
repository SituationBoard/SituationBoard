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
from backend.data.Database import Database
from backend.api.WebSocket import WebSocket
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent

class ActionUpdateDatabase(Action):

    def __init__(self, instanceName: str, settings: Settings, database: Database, webSocket: WebSocket):
        super().__init__("update_database", instanceName, settings)
        self.__database = database
        self.__webSocket = webSocket

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            alarmEvent = sourceEvent
            if alarmEvent.noID:
                self.print("Adding alarm event")
                self.__database.addEvent(alarmEvent)
            else:
                self.print(f"Updating alarm event #{alarmEvent.eventID}")
                self.__database.updateEvent(alarmEvent)
            self.__database.commit()
            self.__webSocket.broadcastDatabaseChanged()
