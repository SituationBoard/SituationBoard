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
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent

class ActionWriteFile(Action):

    def __init__(self, instanceName: str, settings: Settings):
        super().__init__("write_file", instanceName, settings)
        self.__filename = self.getSettingFilename("filename", "alarm.txt")

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            self.writeFile(self.__filename, sourceEvent.raw)

    def writeFile(self, filename: str, content: str) -> None:
        with open(filename, 'w') as file:
            file.write(content)
            file.write("\n")
