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

class AlarmEvent(SourceEvent):
    """AlarmEvents are the most important and most frequent variant of SourceEvents.
    They are created in response to received alarms and contain various information about the alarm event itself.
    As with other SourceEvents, Action plugins can choose to react on AlarmEvents.
    In contrast to other SourceEvents, AlarmEvents can be stored in the database and visualized in the frontend."""

    FLAGS_INVALID = "INVALID"
    FLAGS_VALID   = "VALID"
    FLAGS_BINARY  = "BINARY"

    NO_ID = -1

    def __init__(self, eventID: int = -1) -> None:
        super().__init__()

        self.eventID            = eventID

        self.event              = ""
        self.eventDetails       = ""
        self.location           = ""
        self.locationDetails    = ""
        self.comment            = ""
        self.alarmTimestamp     = ""

        self.locationLatitude   = 0.0 # north/south (-> Y)
        self.locationLongitude  = 0.0 # east/west   (-> X)

        self.flags              = AlarmEvent.FLAGS_INVALID

    @classmethod
    def fromSourceEvent(cls, sourceEvent: SourceEvent, eventID: int = -1) -> "AlarmEvent":
        alarmEvent = cls(eventID)
        alarmEvent.copyDataFrom(sourceEvent)
        alarmEvent.alarmTimestamp = sourceEvent.timestamp
        return alarmEvent

    @property
    def noID(self) -> bool:
        return (self.eventID == AlarmEvent.NO_ID)

    @property
    def valid(self) -> bool:
        return (self.flags == AlarmEvent.FLAGS_VALID)

    @property
    def invalid(self) -> bool:
        return (self.flags == AlarmEvent.FLAGS_INVALID)

    @property
    def binary(self) -> bool:
        return (self.flags == AlarmEvent.FLAGS_BINARY)

    def __str__(self) -> str:
        return f"AlarmEvent Event={self.event} EventID={self.eventID}"

    def __repr__(self) -> str:
        return f"AlarmEvent Event={self.event} EventID={self.eventID}"
