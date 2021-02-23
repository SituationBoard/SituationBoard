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
import string

from typing import List, Optional

from enum import Enum

from backend.util.Settings import Settings
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.event.UnhandledEvent import UnhandledEvent
from backend.event.SourceEvent import SourceEvent
from backend.source.MessageParser import MessageParser

class MessageParserSMS(MessageParser):
    TIMESTAMP_LENGTH_LONG  = 19
    TIMESTAMP_FORMAT_LONG  = "%d.%m.%Y %H:%M:%S"

    TIMESTAMP_LENGTH_SHORT = 16
    TIMESTAMP_FORMAT_SHORT = "%d.%m.%Y %H:%M"

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__("sms", instanceName, settings)
        self.__mergeDuration = self.getSettingInt("merge_duration", 90) # merge non-standard multipart SMS within 90 seconds
        self.__alarmHeader = self.getSettingString("alarm_header", "SMS Alarm")
        self.__alarmSenders = self.getSettingList("alarm_senders", [])

    def parseMessage(self, sourceEvent: SourceEvent, lastEvent: Optional[SourceEvent]) -> Optional[SourceEvent]:
        if self.isEmpty(sourceEvent):
            return None

        if self.hasAlarmHeader(sourceEvent):
            # Alarm header found -> parse alarm message
            return self.parseAlarmMessage(sourceEvent)

        if self.hasSettingHeader(sourceEvent):
            # Setting header found -> parse setting message
            return self.parseSettingMessage(sourceEvent)

        # Bullshit workaround for long (non-standard) multipart SMS (two or more "independent" SMS)
        # -> merge current and last alarm SMS and parse alarm message again
        if (lastEvent is not None) and isinstance(lastEvent, AlarmEvent):
            # last event was an alarm event
            lastAlarm = lastEvent
            if lastAlarm.sender == sourceEvent.sender:
                # last alarm event had the same sender
                tsLast       = datetime.datetime.strptime(lastAlarm.timestamp, AlarmEvent.TIMESTAMP_FORMAT)
                tsCurrent    = datetime.datetime.strptime(sourceEvent.timestamp, AlarmEvent.TIMESTAMP_FORMAT)
                tsDelta      = tsCurrent - tsLast
                deltaSeconds = tsDelta.total_seconds()
                if 0 <= deltaSeconds <= self.__mergeDuration:
                    # last alarm event received not too long ago
                    if self.hasAlarmHeader(lastAlarm):
                        # last alarm event had an alarm header
                        # (we only merge with last alarm events that had an alarm header but it is not required
                        # that the last alarm event was already valid in its incomplete variant)
                        self.print("Merging with previous alarm message (time delta: " + str(deltaSeconds) + " seconds)")
                        lastAlarm.raw = lastAlarm.raw + sourceEvent.raw
                        return self.parseAlarmMessage(lastAlarm)

        # Message with no alarm header but sent from an alarm sender
        if len(self.__alarmSenders) != 0 and sourceEvent.sender in self.__alarmSenders:
            # Return an invalid AlarmEvent (fallback to alarm with raw text)
            return self.fallbackAlarmMessage(sourceEvent)

        # Return an UnhandledEvent (e.g. SMS from telecommunication provider)
        self.error("Received unhandled message (unparsable message - no alarm header, no alarm sender)")
        return UnhandledEvent.fromSourceEvent(sourceEvent, UnhandledEvent.CAUSE_UNPARSABLE_MESSAGE)

    def parseAlarmMessage(self, sourceEvent: SourceEvent) -> AlarmEvent:
        alarmEvent = None
        if isinstance(sourceEvent, AlarmEvent):
            # source event was parsed before and is actually/already a merged alarm event
            # (its former version is thus already stored in the database with a unique ID)
            # -> use the alarm event directly to preserve data like the unique ID
            alarmEvent = sourceEvent
        else:
            # create an alarm event from the new/unparsed source event
            alarmEvent = AlarmEvent.fromSourceEvent(sourceEvent)

        alarmEvent.flags = AlarmEvent.FLAGS_INVALID

        rawLines = self.getRawLines(alarmEvent)

        class ParserState(Enum):
            INITIAL = -1
            TIMESTAMP = 0
            LOCATION_AND_LOCATION_DETAILS = 1
            EVENT_DETAILS = 2
            EVENT = 3
            COMMENT = 4

        activeKeyID = ParserState.INITIAL

        aTimestamp        = ""
        aLocationComplete = ""
        aEvent            = ""
        aEventDetails     = ""
        aComment          = ""

        for line in rawLines:
            # detect new sections through keywords and/or relative line locations ...
            if line.startswith(self.__alarmHeader):
                activeKeyID = ParserState.INITIAL
                continue # skip header (first line)
            if line.startswith('Alarmzeit:'):
                aTimestamp = line.replace('Alarmzeit:', '', 1)
                activeKeyID = ParserState.TIMESTAMP
            elif line.startswith('EO:'):
                aLocationComplete = line.replace('EO:', '', 1)
                # activeKeyID = ParserState.LOCATION_AND_LOCATION_DETAILS # only one line ?
                activeKeyID = ParserState.EVENT_DETAILS # next line is event details (has no prefix)
            # elif line.startswith('SW:'):
            #     aEventDetails = line.replace('SW:', '', 1)
            #     activeKeyID = ParserState.EVENT_DETAILS
            elif line.startswith('STW:'):
                aEvent = line.replace('STW:', '', 1)
                activeKeyID = ParserState.EVENT
            elif line.startswith('Bem:'):
                aComment = line.replace('Bem:', '', 1)
                activeKeyID = ParserState.COMMENT

            # append remaining lines of the active sections to the corresponding variables ...
            elif activeKeyID == ParserState.TIMESTAMP:
                continue # ignore additional timestamp lines
            elif activeKeyID == ParserState.LOCATION_AND_LOCATION_DETAILS:
                aLocationComplete = '\n'.join([aLocationComplete, line])
            elif activeKeyID == ParserState.EVENT_DETAILS:
                aEventDetails = '\n'.join([aEventDetails, line])
            elif activeKeyID == ParserState.EVENT:
                aEvent = '\n'.join([aEvent, line])
            elif activeKeyID == ParserState.COMMENT:
                aComment = '\n'.join([aComment, line])
            else:
                self.error("Parsing error: unknown line, ignoring...")

        alarmEvent.event = aEvent.strip()
        alarmEvent.eventDetails = aEventDetails.strip()
        alarmEvent.comment = aComment.strip()

        aLocationStripped = aLocationComplete.strip(string.whitespace + ",")
        aLocationParts = aLocationStripped.split(",", 2)
        alarmEvent.location = aLocationParts[0].strip() if (len(aLocationParts) > 0) else ""
        alarmEvent.locationDetails = aLocationParts[1].strip() if (len(aLocationParts) > 1) else ""

        try:
            aTimestampStripped = aTimestamp.strip()
            if len(aTimestampStripped) == MessageParserSMS.TIMESTAMP_LENGTH_LONG:
                ats = datetime.datetime.strptime(aTimestampStripped, MessageParserSMS.TIMESTAMP_FORMAT_LONG)
                alarmEvent.alarmTimestamp = ats.strftime(AlarmEvent.TIMESTAMP_FORMAT)
            elif len(aTimestampStripped) == MessageParserSMS.TIMESTAMP_LENGTH_SHORT:
                ats = datetime.datetime.strptime(aTimestampStripped, MessageParserSMS.TIMESTAMP_FORMAT_SHORT)
                alarmEvent.alarmTimestamp = ats.strftime(AlarmEvent.TIMESTAMP_FORMAT)
        except Exception:
            self.error("Parsing error: invalid timestamp format")
            alarmEvent.alarmTimestamp = alarmEvent.timestamp

        # We require three things for a valid alarm event:
        #  - we at least parsed until the beginning of the last field (comment) - and thus end of the event field
        #  - we retrieved at least a (complete) event – we do not care about the event details though
        #  - we retrieved at least a (complete) location - we do not care about the location details though
        if activeKeyID == ParserState.COMMENT and alarmEvent.event != "" and alarmEvent.location != "":
            self.print("Received alarm message (valid)")
            alarmEvent.flags = AlarmEvent.FLAGS_VALID
        else:
            self.error("Received alarm message (invalid - missing information)")
            alarmEvent.flags = AlarmEvent.FLAGS_INVALID

        return alarmEvent

    def fallbackAlarmMessage(self, sourceEvent: SourceEvent) -> AlarmEvent:
        self.error("Received alarm message (invalid - no alarm header)")
        alarmEvent = AlarmEvent.fromSourceEvent(sourceEvent)
        alarmEvent.alarmTimestamp = alarmEvent.timestamp
        alarmEvent.flags = AlarmEvent.FLAGS_INVALID
        return alarmEvent

    def parseSettingMessage(self, sourceEvent: SourceEvent) -> SettingEvent:
        settingEvent = SettingEvent.fromSourceEvent(sourceEvent)
        settingEvent.flags = SettingEvent.FLAGS_INVALID

        rawText = settingEvent.raw
        settingParts = rawText.split("=", 1)
        self.print(f"splitted setting ({settingEvent.raw}) to {settingParts}")

        if len(settingParts) == 2:
            settingEvent.key = settingParts[0].strip()
            settingEvent.value = settingParts[1].strip()
            if settingEvent.key != "":
                settingEvent.flags = SettingEvent.FLAGS_VALID

        self.print("Received setting message")
        return settingEvent

    def isEmpty(self, sourceEvent: SourceEvent) -> bool:
        return sourceEvent.raw is None or sourceEvent.raw == ""

    def getRawLines(self, sourceEvent: SourceEvent) -> List[str]:
        return sourceEvent.raw.split('\n') # split will always return at least [""]

    def hasAlarmHeader(self, sourceEvent: SourceEvent) -> bool:
        rawLines = self.getRawLines(sourceEvent) # rawLines will always contain at least [""]
        return rawLines[0].startswith(self.__alarmHeader)

    def hasSettingHeader(self, sourceEvent: SourceEvent) -> bool:
        rawLines = self.getRawLines(sourceEvent) # rawLines will always contain at least [""]
        return "=" in rawLines[0]
