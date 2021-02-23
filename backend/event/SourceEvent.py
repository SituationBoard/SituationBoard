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

from typing import Dict, Any

class SourceEvent:
    """SourceEvents are a generic representation of events from various sources.
    They are created by SourceDriver plugins upon reception of an event and afterwards handled by Action plugins.
    Depending on the actual event, a SourceEvent or a subclass of SourceEvent (like an AlarmEvent)
    with additional information may be created."""

    SOURCE_UNKNOWN   = "UNKNOWN"
    SOURCE_DUMMY     = "DUMMY"
    SOURCE_MAIL      = "MAIL"
    SOURCE_SMS       = "SMS"
    SOURCE_FAX       = "FAX"
    SOURCE_WEBAPI    = "WEBAPI"
    SOURCE_SCANNER   = "SCANNER"
    SOURCE_MANUAL    = "MANUAL"
    SOURCE_BINARY    = "BINARY"

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        self.source    = SourceEvent.SOURCE_UNKNOWN
        self.sender    = ""
        self.raw       = ""
        self.timestamp = ""

    def copyDataFrom(self, sourceEvent: "SourceEvent") -> None:
        self.source    = sourceEvent.source
        self.sender    = sourceEvent.sender
        self.raw       = sourceEvent.raw
        self.timestamp = sourceEvent.timestamp

    def __str__(self) -> str:
        return f"SourceEvent Source={self.source}"

    def __repr__(self) -> str:
        return f"SourceEvent Source={self.source}"

    def toJSON(self) -> Dict[str, Any]:
        return self.__dict__
