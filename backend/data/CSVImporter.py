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
from backend.event.AlarmEvent import AlarmEvent

class CSVImporter(CSVCommon):

    def __init__(self, database: Database) -> None:
        super().__init__(database, "importer")

    def importEvents(self, filename: str, ignoreFirstLine: bool = True) -> int:
        alarmList = []
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f, delimiter=";", quotechar="\"", doublequote=True)
                alarmList = list(reader)
        except Exception:
            self.fatalContinue(f"Could not read CSV file ({filename})")
            return 1

        line = 0
        importedCount = 0
        invalidCount = 0
        for alarm in alarmList:
            line += 1

            if ignoreFirstLine and line == 1:
                continue

            #TODO: support multiple header lengths (to support file updates and older CSV files):
            #      retrieve column index by column name and provide a default value in case
            #      the CSV file does not contain all fields (e.g. because of an old file format)
            #      Important: adjust documentation accordingly

            if len(alarm) != CSVCommon.TOTAL_COLS:
                invalidCount += 1
                continue

            alarmEvent = AlarmEvent()

            try:
                alarmEvent.timestamp         = self.csv2dbTimestamp(alarm[CSVCommon.COL_TIMESTAMP])
                alarmEvent.event             = self.csv2dbText(alarm[CSVCommon.COL_EVENT])
                alarmEvent.eventDetails      = self.csv2dbText(alarm[CSVCommon.COL_EVENTDETAILS])
                alarmEvent.location          = self.csv2dbText(alarm[CSVCommon.COL_LOCATION])
                alarmEvent.locationDetails   = self.csv2dbText(alarm[CSVCommon.COL_LOCATIONDETAILS])
                alarmEvent.comment           = self.csv2dbText(alarm[CSVCommon.COL_COMMENT])
                alarmEvent.alarmTimestamp    = self.csv2dbTimestamp(alarm[CSVCommon.COL_ALARMTIMESTAMP])
                alarmEvent.locationLatitude  = float(alarm[CSVCommon.COL_LOCATIONLATITUDE])
                alarmEvent.locationLongitude = float(alarm[CSVCommon.COL_LOCATIONLONGITUDE])
                alarmEvent.source            = self.csv2dbText(alarm[CSVCommon.COL_SOURCE])
                alarmEvent.sender            = self.csv2dbText(alarm[CSVCommon.COL_SENDER])
                alarmEvent.raw               = self.csv2dbText(alarm[CSVCommon.COL_RAW])
                alarmEvent.flags             = self.csv2dbText(alarm[CSVCommon.COL_FLAGS])
            except Exception: # invalid timestamp, float, ...
                invalidCount += 1
                continue

            if self._database.addEvent(alarmEvent, verbose=False) < 0:
                invalidCount +=1
                continue

            importedCount += 1

        self.print(f"Imported {importedCount} event(s) into the DB")

        if invalidCount > 0:
            self.error(f"Ignored {invalidCount} invalid line(s)")
            return 1

        return 0
