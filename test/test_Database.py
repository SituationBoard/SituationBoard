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
import copy
import datetime

from backend.util.AppInfo import AppInfo
from backend.data.Database import Database, DatabaseTimespan
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent

class Test_Database:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_database(self) -> None:
        appInfo = AppInfo()
        databaseFilename = os.path.join(appInfo.path, ".temp/situationboard.sqlite")
        maxLastEvents = 10

        # check that creating a database works and yields an empty database
        db = Database(databaseFilename, reset = True)
        assert(db.getEventCount(textOnly = False) == 0)
        assert(db.getEventCount(textOnly = True) == 0)
        assert(db.getEvent(1302) is None)
        assert(len(db.getEvents(textOnly = False)) == 0)
        assert(len(db.getEvents(textOnly = True)) == 0)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = False)) == 0)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = True)) == 0)

        # check for valid stats
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = False) == 0)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = False) == 0)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = False) == 0)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = False) == 0)
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = True) == 0)

        # check that inserting a binary event succeeds
        newEvent1 = self.__createBinaryEvent()
        newEventTemp1 = copy.deepcopy(newEvent1)
        assert(db.updateEvent(newEventTemp1) != 0)
        eventID1 = db.addEvent(newEventTemp1)
        assert(eventID1 != AlarmEvent.NO_ID)
        assert(newEventTemp1.eventID == eventID1)
        assert(db.getEventCount(textOnly = False) == 1)
        assert(db.getEventCount(textOnly = True) == 0)
        assert(len(db.getEvents(textOnly = False)) == 1)
        assert(len(db.getEvents(textOnly = True)) == 0)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = False)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = True)) == 0)
        assert(db.getEvent(eventID1) is not None)

        # check for valid stats
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = True) == 0)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = True) == 0)

        # check that inserting a text event succeeds
        newEvent2 = self.__createTextEvent()
        newEvent2Temp = copy.deepcopy(newEvent2)
        eventID2 = db.addEvent(newEvent2Temp)
        assert(eventID2 != AlarmEvent.NO_ID)
        assert(newEvent2Temp.eventID == eventID2)
        assert(db.getEventCount(textOnly = False) == 2)
        assert(db.getEventCount(textOnly = True) == 1)
        assert(len(db.getEvents(textOnly = False)) == 2)
        assert(len(db.getEvents(textOnly = True)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = False)) == 2)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = True)) == 1)
        assert(db.getEvent(eventID2) is not None)

        # check for valid stats
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = False) == 2)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = False) == 2)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = False) == 2)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = False) == 2)
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly=True) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly=True) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly=True) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly=True) == 1)

        db.commitAndClose()

        # check that reloading a database succeeds and yields existing data
        dbr = Database(databaseFilename, reset = False)
        assert(dbr.getEventCount(textOnly = False) == 2)
        assert(dbr.getEventCount(textOnly = True) == 1)
        assert(len(dbr.getEvents(textOnly = False)) == 2)
        assert(len(dbr.getEvents(textOnly = True)) == 1)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = False)) == 2)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = True)) == 1)

        # check that retrieving an event succeeds after reload succeeds and yields the correct data
        event1 = dbr.getEvent(eventID1)
        assert(event1 is not None)
        assert(isinstance(event1, AlarmEvent))
        assert(event1.eventID == eventID1)
        self.__compareEvents(event1, newEvent1)

        # check that retrieving an event succeeds after reload succeeds and yields the correct data
        event2 = dbr.getEvent(eventID2)
        assert(event2 is not None)
        assert(isinstance(event2, AlarmEvent))
        assert(event2.eventID == eventID2)
        self.__compareEvents(event2, newEvent2)

        # check that updating an event succeeds
        newEvent2Updated = copy.deepcopy(newEvent2Temp)
        self.__updateTextEvent(newEvent2Updated)
        newEvent2UpdatedTemp = copy.deepcopy(newEvent2Updated)
        assert(dbr.updateEvent(newEvent2UpdatedTemp) == 0)
        event2Updated = dbr.getEvent(eventID2)
        assert(event2Updated is not None)
        assert(isinstance(event2Updated, AlarmEvent))
        assert(event2Updated.eventID == eventID2)
        self.__compareEvents(event2Updated, newEvent2Updated)

        # check that deleting an event by ID succeeds
        assert(dbr.removeEventID(eventID1) == 0)
        assert(dbr.getEventCount(textOnly = False) == 1)
        assert(dbr.getEventCount(textOnly = True) == 1)
        assert(dbr.getEvent(eventID1) is None)
        assert(len(dbr.getEvents(textOnly = False)) == 1)
        assert(len(dbr.getEvents(textOnly = True)) == 1)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = False)) == 1)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = True)) == 1)

        # check that deleting an event succeeds
        assert(dbr.removeEvent(newEvent2Updated) == 0)
        assert(dbr.getEventCount(textOnly = False) == 0)
        assert(dbr.getEventCount(textOnly = True) == 0)
        assert(dbr.getEvent(eventID2) is None)
        assert(len(dbr.getEvents(textOnly = False)) == 0)
        assert(len(dbr.getEvents(textOnly = True)) == 0)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = False)) == 0)
        assert(len(dbr.getLastEvents(maxLastEvents, textOnly = True)) == 0)

        # check that deleting non-existent events fails
        assert(dbr.removeEvent(event1) != 0)
        assert(dbr.removeEventID(eventID2) != 0)

        dbr.commitAndClose()

    def __createBinaryEvent(self) -> AlarmEvent:
        moment = datetime.datetime.now()
        timestamp = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)

        newEvent = AlarmEvent()
        newEvent.source = SourceEvent.SOURCE_BINARY
        newEvent.flags = AlarmEvent.FLAGS_BINARY
        newEvent.sender = ""
        newEvent.raw = ""
        newEvent.timestamp = timestamp
        newEvent.event = ""
        newEvent.eventDetails = ""
        newEvent.location = ""
        newEvent.locationDetails = ""
        newEvent.comment = ""
        newEvent.alarmTimestamp = timestamp
        newEvent.locationLatitude = 0.0
        newEvent.locationLongitude = 0.0
        return newEvent

    def __createTextEvent(self) -> AlarmEvent:
        moment = datetime.datetime.now()
        timestamp = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)

        newEvent = AlarmEvent()
        newEvent.source = SourceEvent.SOURCE_SMS
        newEvent.flags = AlarmEvent.FLAGS_VALID
        newEvent.sender = "112"
        newEvent.raw = "raw"
        newEvent.timestamp = timestamp
        newEvent.event = "event"
        newEvent.eventDetails = "eventDetails"
        newEvent.location = "location"
        newEvent.locationDetails = "locationDetails"
        newEvent.comment = "comment"
        newEvent.alarmTimestamp = timestamp
        newEvent.locationLatitude = 1.12
        newEvent.locationLongitude = 13.2
        return newEvent

    def __updateTextEvent(self, event: AlarmEvent) -> AlarmEvent:
        event.comment = "updated comment"
        return event

    def __compareEvents(self, test: AlarmEvent, orig: AlarmEvent) -> None:
        assert(test.source == orig.source)
        assert(test.flags == orig.flags)
        assert(test.sender == orig.sender)
        assert(test.raw == orig.raw)
        assert(test.timestamp == orig.timestamp)
        assert(test.event == orig.event)
        assert(test.eventDetails == orig.eventDetails)
        assert(test.location == orig.location)
        assert(test.locationDetails == orig.locationDetails)
        assert(test.comment == orig.comment)
        assert(test.alarmTimestamp == orig.alarmTimestamp)
        assert(test.locationLatitude == orig.locationLatitude)
        assert(test.locationLongitude == orig.locationLongitude)
