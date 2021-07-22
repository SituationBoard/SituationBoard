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
import sqlite3
import atexit
import datetime

from enum import Enum

from typing import Optional, List, Any, Tuple, NoReturn

from backend.event.AlarmEvent import AlarmEvent

from backend.util.Module import Module

class DatabaseTimespan(Enum):
    TOTAL = "TOTAL"
    YEAR  = "%Y"
    MONTH = "%Y-%m"
    TODAY = "%Y-%m-%d"

class Database(Module):
    """The Database class is responsible for the persistent storage of AlarmEvents in an SQLite file.
    It enables features like the list of recent alarms or the statistics in the frontend.
    AlarmEvents stored in the database can be exported to a CSV file with the CSVExporter.
    In addition, the CSVImporter allows importing events from a CSV file into the database."""

    DB_APPID   = 112
    DB_VERSION = 1

    SCHEMA = """
    CREATE TABLE "alarmevents" (
        "id"                 INTEGER PRIMARY KEY NOT NULL,
        "timestamp"          TEXT,
        "event"              TEXT,
        "eventdetails"       TEXT,
        "location"           TEXT,
        "locationdetails"    TEXT,
        "comment"            TEXT,
        "alarmtimestamp"     TEXT,
        "locationlatitude"   REAL,
        "locationlongitude"  REAL,
        "source"             TEXT,
        "sender"             TEXT,
        "raw"                TEXT,
        "flags"              TEXT
    )
    """

    def __init__(self, filename: str = "", reset: bool = False, commit: bool = True) -> None:
        super().__init__("database", settings = None, debug = False)
        self.__conn: Optional[sqlite3.Connection] = None
        self.__filename = filename

        if filename != "":
            self.init(filename, reset, commit)

    def init(self, filename: str, reset: bool = False, commit: bool = True) -> None:
        if self.__conn is not None:
            self.fatal("Database is already initialized")

        self.__filename = filename

        if commit:
            atexit.register(self.commitAndClose)
        else:
            atexit.register(self.close)

        dbExists = os.path.exists(self.__filename)
        if dbExists and reset:
            self.__deleteExistingDatabase(self.__filename)
            dbExists = False

        if not dbExists:
            self.__conn = self.__createNewDatabase(self.__filename)
            self.__initFile()
        else: #if not self.__conn:
            self.__conn = self.__openExistingDatabase(self.__filename)
            self.__checkFile()

    def __assertInitializedFailed(self) -> NoReturn:
        self.fatal("Database is not yet initialized")

    def __initAlarmEventList(self, eventDataList: List[List[Any]]) -> List[AlarmEvent]:
        eventList = []

        for event in eventDataList:
            newEvent = Database.__alarmEventFromList(event)
            eventList.append(newEvent)

        return eventList

    def __openExistingDatabase(self, filename: str) -> sqlite3.Connection:
        self.print("Opening existing database")
        try:
            conn = sqlite3.connect(filename)
            return conn
        except sqlite3.Error as e:
            self.fatal(f"Failed to open database ({filename})", e)

    def __createNewDatabase(self, filename: str) -> sqlite3.Connection:
        self.print("Creating a new database")
        try:
            conn = sqlite3.connect(filename)
            conn.executescript(Database.SCHEMA)
            return conn
        except sqlite3.Error as e:
            self.fatal(f"Failed to create database ({filename})", e)

    def __deleteExistingDatabase(self, filename: str) -> None:
        self.print("Deleting existing database")
        try:
            os.remove(filename)
        except Exception:
            self.fatal(f"Failed to delete existing database ({filename})")

    def __getAppID(self) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return 0
        query = "pragma application_id"
        cursor = self.__conn.execute(query)
        (dbAppID,) = cursor.fetchone()
        return int(dbAppID)

    def __setAppID(self, appID: int) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return -1
        query = "pragma application_id = " + str(appID)
        cursor = self.__conn.execute(query)
        if cursor.rowcount != 1:
            return 0

        return -1

    def __getVersion(self) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return 0
        query = "pragma user_version"
        cursor = self.__conn.execute(query)
        (dbVersion,) = cursor.fetchone()
        return int(dbVersion)

    def __setVersion(self, version: int) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return -1
        query = "pragma user_version = " + str(version)
        cursor = self.__conn.execute(query)
        if cursor.rowcount != 1:
            return 0

        return -1

    def __initFile(self) -> None:
        if self.__setAppID(Database.DB_APPID) != 0:
            self.fatal("Could not set application ID of database file")
        if self.__setVersion(Database.DB_VERSION) != 0:
            self.fatal("Could not set user version of database file")

        self.commit()

    def __checkFile(self) -> None:
        dbAppID = self.__getAppID()
        dbVersion = self.__getVersion()

        self.dbgPrint("application_id = " + str(dbAppID))
        self.dbgPrint("user_verion = " + str(dbVersion))

        if dbAppID != Database.DB_APPID:
            self.fatal(f"Database file has an invalid application ID (file: id{dbAppID}, expected: id{Database.DB_APPID})")

        if dbVersion > Database.DB_VERSION:
            self.fatal(f"Database file has a user version that is too new (file: v{dbVersion}, supported: v{Database.DB_VERSION})")

        if dbVersion < Database.DB_VERSION:
            pass #TODO: DB version older than current schema -> perform schema update

    def commit(self) -> None:
        if self.__conn:
            self.__conn.commit()
            self.print("Committed database")

    def close(self) -> None:
        if self.__conn:
            self.__conn.close()
            self.__conn = None
            self.print("Closed database")

    def commitAndClose(self) -> None:
        if self.__conn:
            self.__conn.commit()
            self.__conn.close()
            self.__conn = None
            self.print("Committed and closed database")

    def addEvent(self, alarmEvent: AlarmEvent, verbose: bool = True) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return -1

        query = "INSERT INTO alarmevents (timestamp, event, eventdetails, location, locationdetails, comment, " \
                "alarmtimestamp, locationlatitude, locationlongitude, source, sender, raw, flags) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            cursor = self.__conn.execute(query, Database.__tupleWithoutIDFromAlarmEvent(alarmEvent))

            if cursor.rowcount != 1:
                self.error("Could not add alarm event")
                return -1

            alarmEvent.eventID = cursor.lastrowid

            if verbose:
                self.print(f"Added alarm event #{alarmEvent.eventID}")
            return alarmEvent.eventID
        except sqlite3.Error as e:
            self.error("Could not add alarm event", e)
            return -1

    def updateEvent(self, alarmEvent: AlarmEvent, verbose: bool = True) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return -1

        query = "UPDATE alarmevents SET timestamp = ?, event = ?, eventdetails = ?, location = ?, locationdetails = ?, comment = ?, " \
                "alarmtimestamp = ?, locationlatitude = ?, locationlongitude = ?, source = ?, sender = ?, raw = ?, flags = ? " \
                "WHERE id = ?"
        try:
            cursor = self.__conn.execute(query, Database.__tupleWithoutIDFromAlarmEvent(alarmEvent) + (alarmEvent.eventID,))

            if cursor.rowcount != 1:
                self.error(f"Could not update alarm event #{alarmEvent.eventID}")
                return -1

            if verbose:
                self.print(f"Updated alarm event #{alarmEvent.eventID}")
            return 0
        except sqlite3.Error as e:
            self.error(f"Could not update alarm event #{alarmEvent.eventID}", e)
            return -1

    def removeEvent(self, alarmEvent: AlarmEvent) -> int:
        return self.removeEventID(alarmEvent.eventID)

    def removeEventID(self, eventID: int, verbose: bool = True) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return -1

        query = "DELETE FROM alarmevents WHERE id = ?"
        try:
            cursor = self.__conn.execute(query, (eventID,))

            if cursor.rowcount != 1:
                self.error(f"Could not remove alarm event #{eventID}")
                return -1

            if verbose:
                self.print(f"Removed alarm event #{eventID}")
            return 0
        except sqlite3.Error as e:
            self.error(f"Could not remove alarm event #{eventID}", e)
            return -1

    def getEvent(self, eventID: int) -> Optional[AlarmEvent]:
        if self.__conn is None: self.__assertInitializedFailed() # return None

        query = "SELECT * FROM alarmevents WHERE id = ?"
        cursor = self.__conn.execute(query, (eventID,))
        result = cursor.fetchone()
        if result is not None:
            return Database.__alarmEventFromList(result)

        return None

    def getEvents(self, textOnly: bool) -> List[AlarmEvent]:
        if self.__conn is None: self.__assertInitializedFailed() # return []

        if textOnly:
            query = "SELECT * FROM alarmevents WHERE FLAGS != '" + AlarmEvent.FLAGS_BINARY + "' ORDER BY id ASC"
        else:
            query = "SELECT * FROM alarmevents ORDER BY id ASC"
        cursor = self.__conn.execute(query)
        result = cursor.fetchall()
        return self.__initAlarmEventList(result)

    def getLastEvents(self, count: int, textOnly: bool) -> List[AlarmEvent]:
        if self.__conn is None: self.__assertInitializedFailed() # return []

        if textOnly:
            query = "SELECT * FROM alarmevents WHERE FLAGS != '" + AlarmEvent.FLAGS_BINARY + "' ORDER BY id DESC LIMIT ?"
        else:
            query = "SELECT * FROM alarmevents ORDER BY id DESC LIMIT ?"
        cursor = self.__conn.execute(query, (count,))
        result = cursor.fetchall()
        return self.__initAlarmEventList(result)

    def getEventCount(self, textOnly: bool) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return 0

        if textOnly:
            query = "SELECT COUNT(*) FROM alarmevents WHERE FLAGS != '" + AlarmEvent.FLAGS_BINARY + "'"
        else:
            query = "SELECT COUNT(*) FROM alarmevents"
        cursor = self.__conn.execute(query)
        (count,) = cursor.fetchone()
        return int(count)

    def getEventStats(self, timespan: DatabaseTimespan, textOnly: bool) -> int:
        if self.__conn is None: self.__assertInitializedFailed() # return 0

        if timespan == DatabaseTimespan.TOTAL:
            return self.getEventCount(textOnly=textOnly)

        moment = datetime.datetime.now()
        currentTimespan = moment.strftime(timespan.value)
        if textOnly:
            query = "SELECT COUNT(*) FROM alarmevents WHERE FLAGS != '" + AlarmEvent.FLAGS_BINARY + "' AND strftime('" + timespan.value + "', alarmtimestamp) == ?"
        else:
            query = "SELECT COUNT(*) FROM alarmevents WHERE strftime('" + timespan.value + "', alarmtimestamp) == ?"
        cursor = self.__conn.execute(query, (currentTimespan,))
        (count,) = cursor.fetchone()
        return int(count)

    @classmethod
    def __tupleWithoutIDFromAlarmEvent(cls, alarmEvent: AlarmEvent) -> Tuple[Any, ...]:
        return (
            alarmEvent.timestamp,

            alarmEvent.event,
            alarmEvent.eventDetails,
            alarmEvent.location,
            alarmEvent.locationDetails,
            alarmEvent.comment,
            alarmEvent.alarmTimestamp,
            alarmEvent.locationLatitude,
            alarmEvent.locationLongitude,

            alarmEvent.source,
            alarmEvent.sender,
            alarmEvent.raw,
            alarmEvent.flags)

    #pylint: disable=unused-private-member
    @classmethod
    def __tupleWithIDFromAlarmEvent(cls, alarmEvent: AlarmEvent) -> Tuple[Any, ...]:
        return (alarmEvent.eventID,) + cls.__tupleWithoutIDFromAlarmEvent(alarmEvent)

    @classmethod
    def __alarmEventFromList(cls, eventData: List[Any]) -> AlarmEvent:
        alarmEvent = AlarmEvent(eventData[0])

        alarmEvent.timestamp          = eventData[1]

        alarmEvent.event              = eventData[2]
        alarmEvent.eventDetails       = eventData[3]
        alarmEvent.location           = eventData[4]
        alarmEvent.locationDetails    = eventData[5]
        alarmEvent.comment            = eventData[6]
        alarmEvent.alarmTimestamp     = eventData[7]
        alarmEvent.locationLatitude   = eventData[8]
        alarmEvent.locationLongitude  = eventData[9]

        alarmEvent.source             = eventData[10]
        alarmEvent.sender             = eventData[11]
        alarmEvent.raw                = eventData[12]
        alarmEvent.flags              = eventData[13]

        return alarmEvent
