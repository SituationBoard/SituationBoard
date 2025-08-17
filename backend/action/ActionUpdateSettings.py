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
from backend.event.SourceEvent import SourceEvent
from backend.event.SettingEvent import SettingEvent

class ActionUpdateSettings(Action):

    def __init__(self, instanceName: str, settings: Settings):
        super().__init__("update_settings", instanceName, settings)
        self.__storeChanges = self.getSettingBoolean("store_changes", True)

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, SettingEvent):
            settingEvent = sourceEvent
            settingName  = settingEvent.key.lower()
            settingValue = settingEvent.value
            settingValueSingleLine = StringConverter.string2singleline(settingValue)

            if settingName == "header":
                self.print(f"Updating setting {settingName} with value {settingValueSingleLine}")
                self.settings.setFrontendHeader(settingValue)
                if self.__storeChanges:
                    self.settings.store()
            elif settingName == "news":
                self.print(f"Updating setting {settingName} with value {settingValueSingleLine}")
                self.settings.setFrontendNews(settingValue)
                if self.__storeChanges:
                    self.settings.store()
            else:
                self.error(f"Invalid setting {settingName} (value: {settingValueSingleLine})")
