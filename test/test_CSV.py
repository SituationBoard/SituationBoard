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

import os
import filecmp
import datetime

from backend.util.AppInfo import AppInfo
from backend.data.CSVImporter import CSVImporter
from backend.data.CSVExporter import CSVExporter
from backend.data.Database import Database
from backend.event.AlarmEvent import AlarmEvent

class Test_CSV:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_csv(self) -> None:
        appInfo = AppInfo()
        dbFilename = os.path.join(appInfo.path, ".temp/situationboard.sqlite")
        inFilename = os.path.join(appInfo.path, "docs/dummy.csv")
        outFilename = os.path.join(appInfo.path, ".temp/dummy.csv")
        csvFilename = os.path.join(appInfo.path, ".temp/corner.csv")

        ###### TEST 1 (round trip) ######

        # create a new (empty) database
        d = Database(dbFilename, reset = True)
        assert(d.getEventCount(textOnly = False) == 0)

        # import data from CSV
        i = CSVImporter(d)
        result = i.importEvents(inFilename)
        assert(result == 0)
        assert(d.getEventCount(textOnly = False) > 0)

        # export data to CSV
        e = CSVExporter(d)
        result = e.exportEvents(outFilename)
        assert(result == 0)

        # compare CSV files
        assert(filecmp.cmp(inFilename, outFilename, shallow=False))

        # close database
        d.close()

        ###### TEST 2 (corner cases) ######

        # create a new (empty) database
        d = Database(dbFilename, reset = True)
        assert(d.getEventCount(textOnly = False) == 0)

        # add new event with pathologic content
        ts = datetime.datetime.now().strftime(AlarmEvent.TIMESTAMP_FORMAT)
        content = "Test\n;\\Test\nTest\"äöüß\"\"äöüß'äöüß''äöüß\näöüß"

        aeAdded = AlarmEvent()
        aeAdded.timestamp = ts
        aeAdded.event = content
        aeAdded.eventDetails = content
        aeAdded.location = content
        aeAdded.locationDetails = content
        aeAdded.comment = content
        aeAdded.alarmTimestamp = ts
        aeAdded.locationLatitude = 1.12
        aeAdded.locationLongitude = -13.2
        aeAdded.flags = AlarmEvent.FLAGS_VALID
        aeAdded.source = AlarmEvent.SOURCE_DUMMY
        aeAdded.raw = "{\n\"test\": \"test;:test;:test\"\n}"
        eventID = d.addEvent(aeAdded)

        # export data to CSV
        e = CSVExporter(d)
        result = e.exportEvents(csvFilename)
        assert(result == 0)

        # close database
        d.close()

        # create a new (empty) database
        d = Database(dbFilename, reset = True)

        # import data from CSV
        i = CSVImporter(d)
        result = i.importEvents(csvFilename)
        assert(result == 0)
        assert(d.getEventCount(textOnly = False) > 0)

        # load event
        aeLoaded = d.getEvent(eventID)
        assert(aeLoaded is not None)

        # compare event data
        assert(aeAdded.timestamp == aeLoaded.timestamp)
        assert(aeAdded.event == aeLoaded.event)
        assert(aeAdded.eventDetails == aeLoaded.eventDetails)
        assert(aeAdded.location == aeLoaded.location)
        assert(aeAdded.locationDetails == aeLoaded.locationDetails)
        assert(aeAdded.comment == aeLoaded.comment)
        assert(aeAdded.alarmTimestamp == aeLoaded.alarmTimestamp)
        assert(aeAdded.locationLatitude == aeLoaded.locationLatitude)
        assert(aeAdded.locationLongitude == aeLoaded.locationLongitude)
        assert(aeAdded.flags == aeLoaded.flags)
        assert(aeAdded.source == aeLoaded.source)
        assert(aeAdded.raw == aeLoaded.raw)

        # close database
        d.close()
