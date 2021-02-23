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

from backend.util.Module import Module
from backend.util.StringConverter import StringConverter
from backend.data.Database import Database

from backend.event.AlarmEvent import AlarmEvent

class CSVCommon(Module):
    COL_TIMESTAMP          = 0  # SourceEvent
    COL_EVENT              = 1  # AlarmEvent
    COL_EVENTDETAILS       = 2  # AlarmEvent
    COL_LOCATION           = 3  # AlarmEvent
    COL_LOCATIONDETAILS    = 4  # AlarmEvent
    COL_COMMENT            = 5  # AlarmEvent
    COL_ALARMTIMESTAMP     = 6  # AlarmEvent
    COL_LOCATIONLATITUDE   = 7  # AlarmEvent
    COL_LOCATIONLONGITUDE  = 8  # AlarmEvent
    COL_SOURCE             = 9  # SourceEvent
    COL_SENDER             = 10 # SourceEvent
    COL_RAW                = 11 # SourceEvent
    COL_FLAGS              = 12 # AlarmEvent
    TOTAL_COLS             = 13

    TIMESTAMP_FORMAT_EXTERNAL = "%Y-%m-%d %H:%M:%S" # "%d.%m.%Y %H:%M"

    def __init__(self, database: Database, name: str) -> None:
        super().__init__(name, settings = None, debug = False)
        self._database = database

    @staticmethod
    def db2csvText(dbText: str) -> str:
        return StringConverter.string2singleline(dbText)

    @staticmethod
    def csv2dbText(csvText: str) -> str:
        return StringConverter.singleline2string(csvText)

    @staticmethod
    def db2csvTimestamp(dbTimestamp: str) -> str:
        timestamp = datetime.datetime.strptime(dbTimestamp, AlarmEvent.TIMESTAMP_FORMAT)
        return timestamp.strftime(CSVCommon.TIMESTAMP_FORMAT_EXTERNAL)

    @staticmethod
    def csv2dbTimestamp(csvTimestamp: str) -> str:
        timestamp = datetime.datetime.strptime(csvTimestamp, CSVCommon.TIMESTAMP_FORMAT_EXTERNAL)
        return timestamp.strftime(AlarmEvent.TIMESTAMP_FORMAT)
