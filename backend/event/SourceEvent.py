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

import datetime

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
    SOURCE_DIVERA    = "DIVERA"
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
        self.wasHandledOnce = False # Will be set to True once all handlers were provided with the AlarmEvent for the first time

    def copyDataFrom(self, sourceEvent: "SourceEvent") -> None:
        self.source    = sourceEvent.source
        self.sender    = sourceEvent.sender
        self.raw       = sourceEvent.raw
        self.timestamp = sourceEvent.timestamp
        self.wasHandledOnce = sourceEvent.wasHandledOnce

    def markAsHandled(self) -> None:
        """This method is called after every Action handler was provided with
        the SourceEvent to handle it (for the first time)."""
        self.wasHandledOnce = True

    @property
    def updated(self) -> bool:
        """This allows Actions to identify whether an event is actually new or
        whether it was only updated by the SourceDriver and was handled before."""
        return self.wasHandledOnce

    def isOutdated(self, maxAgeInSeconds: int) -> bool:
        """This method allows Actions to check whether an event is recent and should actually trigger an action
        or whether it is outdated/delayed and should possibly be ignored based on a maximum age."""
        if maxAgeInSeconds <= 0:
            return False

        if self.timestamp == "":
            return False

        try:
            eventTS = datetime.datetime.strptime(self.timestamp, SourceEvent.TIMESTAMP_FORMAT)
        except Exception:
            return False

        nowTS = datetime.datetime.now()
        age = nowTS - eventTS
        if age.total_seconds() > maxAgeInSeconds:
            return True

        return False

    def toJSON(self) -> Dict[str, Any]:
        return self.__dict__

    def __str__(self) -> str:
        return f"SourceEvent Source={self.source}"

    def __repr__(self) -> str:
        return f"SourceEvent Source={self.source}"
