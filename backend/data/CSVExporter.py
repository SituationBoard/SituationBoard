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

import csv

from backend.data.CSVCommon import CSVCommon
from backend.data.Database import Database

class CSVExporter(CSVCommon):

    def __init__(self, database: Database) -> None:
        super().__init__(database, "exporter")

    def exportEvents(self, filename: str, printHeader: bool = True) -> int:

        try:
            exportedCount = 0

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=";", quotechar="\"", doublequote=True)

                if printHeader:
                    line = [""] * CSVCommon.TOTAL_COLS
                    line[CSVCommon.COL_TIMESTAMP]         = "Timestamp"
                    line[CSVCommon.COL_EVENT]             = "Event"
                    line[CSVCommon.COL_EVENTDETAILS]      = "EventDetails"
                    line[CSVCommon.COL_LOCATION]          = "Location"
                    line[CSVCommon.COL_LOCATIONDETAILS]   = "LocationDetails"
                    line[CSVCommon.COL_COMMENT]           = "Comment"
                    line[CSVCommon.COL_ALARMTIMESTAMP]    = "AlarmTimestamp"
                    line[CSVCommon.COL_LOCATIONLATITUDE]  = "LocationLatitude"
                    line[CSVCommon.COL_LOCATIONLONGITUDE] = "LocationLongitude"
                    line[CSVCommon.COL_SOURCE]            = "Source"
                    line[CSVCommon.COL_SENDER]            = "Sender"
                    line[CSVCommon.COL_RAW]               = "Raw"
                    line[CSVCommon.COL_FLAGS]             = "Flags"
                    writer.writerow(line)

                alarmEvents = self._database.getEvents(textOnly = False)

                for alarm in alarmEvents:
                    line = [""] * CSVExporter.TOTAL_COLS
                    line[CSVCommon.COL_TIMESTAMP]         = self.db2csvTimestamp(alarm.timestamp)
                    line[CSVCommon.COL_EVENT]             = self.db2csvText(alarm.event)
                    line[CSVCommon.COL_EVENTDETAILS]      = self.db2csvText(alarm.eventDetails)
                    line[CSVCommon.COL_LOCATION]          = self.db2csvText(alarm.location)
                    line[CSVCommon.COL_LOCATIONDETAILS]   = self.db2csvText(alarm.locationDetails)
                    line[CSVCommon.COL_COMMENT]           = self.db2csvText(alarm.comment)
                    line[CSVCommon.COL_ALARMTIMESTAMP]    = self.db2csvTimestamp(alarm.alarmTimestamp)
                    line[CSVCommon.COL_LOCATIONLATITUDE]  = str(alarm.locationLatitude)
                    line[CSVCommon.COL_LOCATIONLONGITUDE] = str(alarm.locationLongitude)
                    line[CSVCommon.COL_SOURCE]            = self.db2csvText(alarm.source)
                    line[CSVCommon.COL_SENDER]            = self.db2csvText(alarm.sender)
                    line[CSVCommon.COL_RAW]               = self.db2csvText(alarm.raw)
                    line[CSVCommon.COL_FLAGS]             = self.db2csvText(alarm.flags)
                    writer.writerow(line)
                    exportedCount += 1

            self.print(f"Exported {exportedCount} event(s) from the DB")
            return 0

        except Exception:
            self.fatalContinue(f"Could not write CSV file ({filename})")
            return 1
