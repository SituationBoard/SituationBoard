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

from backend.event.SourceEvent import SourceEvent

class SettingEvent(SourceEvent):
    """SettingEvents represent user requests to update specific settings.
    They allow source-specific mechanisms/messages to interact with the system (e.g. update the news line in the frontend).
    As with other SourceEvents, Action plugins can choose to react on SettingEvents."""

    FLAGS_INVALID = "INVALID"
    FLAGS_VALID   = "VALID"

    def __init__(self) -> None:
        super().__init__()

        self.key   = ""
        self.value = ""

        self.flags = SettingEvent.FLAGS_INVALID

    @classmethod
    def fromSourceEvent(cls, sourceEvent: SourceEvent) -> "SettingEvent":
        settingEvent = cls()
        settingEvent.copyDataFrom(sourceEvent)
        return settingEvent

    @property
    def valid(self) -> bool:
        return (self.flags == SettingEvent.FLAGS_VALID)

    @property
    def invalid(self) -> bool:
        return (self.flags == SettingEvent.FLAGS_INVALID)

    def __str__(self) -> str:
        return f"SettingEvent {self.key}={self.value}"

    def __repr__(self) -> str:
        return f"SettingEvent {self.key}={self.value}"
