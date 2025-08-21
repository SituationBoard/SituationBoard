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
import datetime
import shutil

from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.source.MessageParserSMS import MessageParserSMS

from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.event.UnhandledEvent import UnhandledEvent

class Test_MessageParserSMS:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        s = Settings(settingsFilename, appInfo.path)

        self.p = MessageParserSMS("", s)

        self.defaultSender = "112"
        self.alarmSender = "+49112" # alarm sender set in config
        self.settingSender = "123"
        self.defaultTimestamp = datetime.datetime.now().strftime(AlarmEvent.TIMESTAMP_FORMAT)
        self.eid = 1302

    def __new_message(self, raw: str, sender: str = "", timestamp: str = "", source: str = "") -> SourceEvent:
        sourceEvent = SourceEvent()
        sourceEvent.source = source if source != "" else SourceEvent.SOURCE_SMS
        sourceEvent.raw = raw
        sourceEvent.sender = sender if sender != "" else self.defaultSender
        sourceEvent.timestamp = timestamp if timestamp != "" else self.defaultTimestamp
        return sourceEvent

    def __check_original(self, sourceEvent: SourceEvent, raw: str, sender: str = "", timestamp: str = "", source: str = "") -> None: #pylint: disable=too-many-positional-arguments
        source = source if source != "" else SourceEvent.SOURCE_SMS
        sender = sender if sender != "" else self.defaultSender
        timestamp = timestamp if timestamp != "" else self.defaultTimestamp
        assert(sourceEvent.source == source)
        assert(sourceEvent.raw == raw)
        assert(sourceEvent.sender == sender)
        assert(sourceEvent.timestamp == timestamp)

    def __check_alarm_empty(self, alarmEvent: AlarmEvent, timestamp: str = "") -> None:
        timestamp = timestamp if timestamp != "" else self.defaultTimestamp
        assert(alarmEvent.alarmTimestamp == timestamp)
        assert(alarmEvent.event == "")
        assert(alarmEvent.eventDetails == "")
        assert(alarmEvent.location == "")
        assert(alarmEvent.locationDetails == "")
        assert(alarmEvent.comment == "")
        assert(alarmEvent.noID)

    def test_empty_message(self) -> None:
        # parse empty message (should return None)
        sms = ""
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(m is None)

    def test_empty_message_alarm_sender(self) -> None:
        # parse empty message from alarm sender (should return None)
        sms = ""
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(m is None)

    def test_unhandled_invalid_header(self) -> None:
        # parse unhandled event (invalid header and not from alarm sender)
        sms = "test112"
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, UnhandledEvent))
        self.__check_original(m, sms)
        assert(m.unparsable)

    def test_invalid_alarm_event_alarm_sender(self) -> None:
        # parse invalid alarm event (invalid header but from alarm sender)
        sms = "test112"
        se = self.__new_message(sms, sender=self.alarmSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, AlarmEvent))
        self.__check_original(m, sms, sender=self.alarmSender)
        assert(m.invalid)
        self.__check_alarm_empty(m)

    def test_invalid_alarm_event_incomplete(self) -> None:
        # parse invalid alarm event (correct header but parsing event and location failed)
        sms = "SMS Alarm\nNOTHING HERE"
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, AlarmEvent))
        self.__check_original(m, sms)
        assert(m.invalid)
        self.__check_alarm_empty(m)

    def test_valid_alarm_event(self) -> None:
        # parse valid alarm event (correct header, successful parsing, any sender)
        sms = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent details\nSTW: event\nBem: comment\ncomment\ncomment"
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, AlarmEvent))
        self.__check_original(m, sms)
        assert(m.valid)
        assert(m.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m.event == "event")
        assert(m.eventDetails == "event details")
        assert(m.location == "location")
        assert(m.locationDetails == "location details")
        assert(m.comment == "comment\ncomment\ncomment")
        assert(m.noID)

    def test_valid_alarm_event_invalid_timestamp(self) -> None:
        # parse valid alarm event with invalid timestamp (correct header, successful parsing, any sender)
        sms = "SMS Alarm\nAlarmzeit: 24.06.ABCD 01:02:03\nEO: location, location details\nevent details\nSTW: event\nBem: comment\ncomment\ncomment"
        se = self.__new_message(sms)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, AlarmEvent))
        self.__check_original(m, sms)
        assert(m.valid)
        assert(m.alarmTimestamp == self.defaultTimestamp)
        assert(m.event == "event")
        assert(m.eventDetails == "event details")
        assert(m.location == "location")
        assert(m.locationDetails == "location details")
        assert(m.comment == "comment\ncomment\ncomment")
        assert(m.noID)

    def test_valid_alarm_event_merged_after_invalid(self) -> None:
        # parse valid alarm event after merging an invalid part and the remaining part
        sms1 = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent det"
        sms2 = "ails\nSTW: event\nBem: comment\ncomment\ncomment"

        se1 = self.__new_message(sms1)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1)
        assert(m1.invalid)
        assert(m1.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m1.event == "")
        assert(m1.eventDetails == "event det")
        assert(m1.location == "location")
        assert(m1.locationDetails == "location details")
        assert(m1.comment == "")
        assert(m1.noID)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms1 + sms2)
        assert(m2.valid)
        assert(m2.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m2.event == "event")
        assert(m2.eventDetails == "event details")
        assert(m2.location == "location")
        assert(m2.locationDetails == "location details")
        assert(m2.comment == "comment\ncomment\ncomment")
        assert(m2.eventID == self.eid)
        assert(m2 is m1)

    def test_valid_alarm_event_merged_after_almost_valid(self) -> None:
        # parse valid alarm event after merging an invalid part (almost complete but missing the last part of the event) and the remaining part
        sms1 = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent details\nSTW: eve"
        sms2 = "nt\nBem: comment\ncomment\ncomment"

        se1 = self.__new_message(sms1)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1)
        assert(m1.invalid)
        assert(m1.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m1.event == "eve")
        assert(m1.eventDetails == "event details")
        assert(m1.location == "location")
        assert(m1.locationDetails == "location details")
        assert(m1.comment == "")
        assert(m1.noID)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms1 + sms2)
        assert(m2.valid)
        assert(m2.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m2.event == "event")
        assert(m2.eventDetails == "event details")
        assert(m2.location == "location")
        assert(m2.locationDetails == "location details")
        assert(m2.comment == "comment\ncomment\ncomment")
        assert(m2.eventID == self.eid)
        assert(m2 is m1)

    def test_valid_alarm_event_merged_after_valid(self) -> None:
        # parse valid alarm event after merging a valid part and the remaining part
        sms1 = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent details\nSTW: event\nBem: comment\n"
        sms2 = "comment\ncomment"

        se1 = self.__new_message(sms1)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1)
        assert(m1.valid)
        assert(m1.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m1.event == "event")
        assert(m1.eventDetails == "event details")
        assert(m1.location == "location")
        assert(m1.locationDetails == "location details")
        assert(m1.comment == "comment")
        assert(m1.noID)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms1 + sms2)
        assert(m2.valid)
        assert(m2.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m2.event == "event")
        assert(m2.eventDetails == "event details")
        assert(m2.location == "location")
        assert(m2.locationDetails == "location details")
        assert(m2.comment == "comment\ncomment\ncomment")
        assert(m2.eventID == self.eid)
        assert(m2 is m1)

    def test_valid_alarm_event_not_merged_two_valid(self) -> None:
        # parse valid alarm event after not merging with another valid alarm event
        sms1 = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent details\nSTW: event1\nBem: comment one"
        sms2 = "SMS Alarm\nAlarmzeit: 24.06.2020 01:02:03\nEO: location, location details\nevent details\nSTW: event2\nBem: comment two"

        se1 = self.__new_message(sms1)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1)
        assert(m1.valid)
        assert(m1.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m1.event == "event1")
        assert(m1.eventDetails == "event details")
        assert(m1.location == "location")
        assert(m1.locationDetails == "location details")
        assert(m1.comment == "comment one")
        assert(m1.noID)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms2)
        assert(m2.valid)
        assert(m2.alarmTimestamp == "2020-06-24 01:02:03")
        assert(m2.event == "event2")
        assert(m2.eventDetails == "event details")
        assert(m2.location == "location")
        assert(m2.locationDetails == "location details")
        assert(m2.comment == "comment two")
        assert(m2.noID)
        assert(m2 is not m1)

    def test_valid_alarm_event_not_merged_different_senders(self) -> None:
        # parse invalid alarm event after not merging with another valid alarm event from a different sender
        sms1 = "SMS Alarm\nAlarmzeit: 24.06.2019 01:02:03\nEO: location, location details\nevent details\nSTW: event1\nBem: comment one"
        sms2 = "FALLBACK"

        se1 = self.__new_message(sms1)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1)
        assert(m1.valid)
        assert(m1.alarmTimestamp == "2019-06-24 01:02:03")
        assert(m1.event == "event1")
        assert(m1.eventDetails == "event details")
        assert(m1.location == "location")
        assert(m1.locationDetails == "location details")
        assert(m1.comment == "comment one")
        assert(m1.noID)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2, sender=self.alarmSender)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms2, sender=self.alarmSender)
        assert(m2.invalid)
        self.__check_alarm_empty(m2)
        assert(m2 is not m1)

    def test_valid_alarm_event_not_merged_first_no_header(self) -> None:
        # parse valid alarm event after not merging with another valid alarm event
        sms1 = "FALLBACK"
        sms2 = "SMS Alarm\nAlarmzeit: 24.06.2020 01:02:03\nEO: location, location details\nevent details\nSTW: event2\nBem: comment\ncomment\ncomment"

        se1 = self.__new_message(sms1, sender=self.alarmSender)
        m1 = self.p.parseMessage(se1, None)
        assert(isinstance(m1, AlarmEvent))
        self.__check_original(m1, sms1, sender=self.alarmSender)
        assert(m1.invalid)
        self.__check_alarm_empty(m1)
        m1.eventID = self.eid

        se2 = self.__new_message(sms2, sender=self.alarmSender)
        m2 = self.p.parseMessage(se2, m1)
        assert(isinstance(m2, AlarmEvent))
        self.__check_original(m2, sms2, sender=self.alarmSender)
        assert(m2.valid)
        assert(m2.alarmTimestamp == "2020-06-24 01:02:03")
        assert(m2.event == "event2")
        assert(m2.eventDetails == "event details")
        assert(m2.location == "location")
        assert(m2.locationDetails == "location details")
        assert(m2.comment == "comment\ncomment\ncomment")
        assert(m2.noID)
        assert(m2 is not m1)

    def test_invalid_setting_event_no_key(self) -> None:
        # parse invalid settings event (no key, only value)
        sms = "=a b"
        se = self.__new_message(sms, sender=self.settingSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, SettingEvent))
        self.__check_original(m, sms, sender=self.settingSender)
        assert(m.invalid)
        assert(m.key == "")
        assert(m.value == "a b")

    def test_invalid_setting_event_no_key_no_value(self) -> None:
        # parse invalid settings event (no key, no value)
        sms = "="
        se = self.__new_message(sms, sender=self.settingSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, SettingEvent))
        self.__check_original(m, sms, sender=self.settingSender)
        assert(m.invalid)
        assert(m.key == "")
        assert(m.value == "")

    def test_valid_setting_event_no_value(self) -> None:
        # parse valid settings event (only key, no value)
        sms = "key="
        se = self.__new_message(sms, sender=self.settingSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, SettingEvent))
        self.__check_original(m, sms, sender=self.settingSender)
        assert(m.valid)
        assert(m.key == "key")
        assert(m.value == "")

    def test_valid_setting_event_multiline_value(self) -> None:
        # parse valid settings event (key and multiline value)
        sms = "key=a b\nc d"
        se = self.__new_message(sms, sender=self.settingSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, SettingEvent))
        self.__check_original(m, sms, sender=self.settingSender)
        assert(m.valid)
        assert(m.key == "key")
        assert(m.value == "a b\nc d")

    def test_valid_setting_event(self) -> None:
        # parse valid settings event (key and value with =)
        sms = "key=a b=c d"
        se = self.__new_message(sms, sender=self.settingSender)
        m = self.p.parseMessage(se, None)
        assert(isinstance(m, SettingEvent))
        self.__check_original(m, sms, sender=self.settingSender)
        assert(m.valid)
        assert(m.key == "key")
        assert(m.value == "a b=c d")
