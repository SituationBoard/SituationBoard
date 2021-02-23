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

class UnhandledEvent(SourceEvent):
    """UnhandledEvents represent SourceEvents that could not be parsed or are unhandled for other reasons
    (like an event sender that was ignored because of the allowlist/denylist).
    Although their name may suggest otherwise, Action plugins can still choose to react on UnhandledEvents
    (e.g. to log their occurrence or to inform a system administrator)."""

    CAUSE_UNPARSABLE_MESSAGE = "UNPARSABLE_MESSAGE"
    CAUSE_IGNORED_SENDER     = "IGNORED_SENDER"

    def __init__(self, cause: str) -> None:
        super().__init__()

        self.cause = cause

    @property
    def unparsable(self) -> bool:
        return (self.cause == UnhandledEvent.CAUSE_UNPARSABLE_MESSAGE)

    @property
    def ignored(self) -> bool:
        return (self.cause == UnhandledEvent.CAUSE_IGNORED_SENDER)

    @classmethod
    def fromSourceEvent(cls, sourceEvent: SourceEvent, cause: str) -> "UnhandledEvent":
        unhandledEvent = cls(cause)
        unhandledEvent.copyDataFrom(sourceEvent)
        return unhandledEvent

    def __str__(self) -> str:
        return f"UnhandledEvent Cause={self.cause}"

    def __repr__(self) -> str:
        return f"UnhandledEvent Cause={self.cause}"
