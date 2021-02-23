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
import shutil
import datetime

from backend.api.WebSocket import WebSocket
from backend.data.Database import Database, DatabaseTimespan
from backend.util.AppInfo import AppInfo
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.util.PluginManager import PluginManager
from backend.util.Settings import Settings
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent
from backend.action.ActionUpdateDatabase import ActionUpdateDatabase

class Test_ActionUpdateDatabase:

    UPDATED_COMMENT = "updated comment"

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_handle_event(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")
        databaseFilename = os.path.join(appInfo.path,".temp/situationboard.sqlite")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        settings = Settings(settingsFilename, appInfo.path)

        maxLastEvents = 10

        displayPowerManager = DisplayPowerManager(settings)

        db = Database(databaseFilename, reset = True)

        webSocket = WebSocket(appInfo, settings, db)

        pluginManager = PluginManager(settings, db, webSocket, displayPowerManager)

        webSocket.init(pluginManager)

        # check that creating a database works and yields an empty database
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

        action = ActionUpdateDatabase("", settings, db, webSocket)

        # check that inserting an alarm event succeeds
        newEvent = self.__createEvent()
        action.handleEvent(newEvent)
        assert(not newEvent.noID)
        assert(db.getEventCount(textOnly = False) == 1)
        assert(db.getEventCount(textOnly = True) == 1)
        assert(len(db.getEvents(textOnly = False)) == 1)
        assert(len(db.getEvents(textOnly = True)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = False)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = True)) == 1)
        newEventID = newEvent.eventID
        assert(db.getEvent(newEventID) is not None)

        # check for valid stats
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = True) == 1)

        # check that updating an alarm event succeeds
        self.__updateEvent(newEvent)
        action.handleEvent(newEvent)
        assert(newEvent.eventID == newEventID)
        assert(db.getEventCount(textOnly = False) == 1)
        assert(db.getEventCount(textOnly = True) == 1)
        assert(len(db.getEvents(textOnly = False)) == 1)
        assert(len(db.getEvents(textOnly = True)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = False)) == 1)
        assert(len(db.getLastEvents(maxLastEvents, textOnly = True)) == 1)
        retrievedEvent = db.getEvent(newEventID)
        assert(retrievedEvent is not None)
        assert(retrievedEvent.comment == Test_ActionUpdateDatabase.UPDATED_COMMENT)

        # check for valid stats
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = False) == 1)
        assert(db.getEventStats(DatabaseTimespan.TOTAL, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.YEAR, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.MONTH, textOnly = True) == 1)
        assert(db.getEventStats(DatabaseTimespan.TODAY, textOnly = True) == 1)

        db.commitAndClose()

    def __createEvent(self) -> AlarmEvent:
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

    def __updateEvent(self, event: AlarmEvent) -> AlarmEvent:
        event.comment = Test_ActionUpdateDatabase.UPDATED_COMMENT
        return event
