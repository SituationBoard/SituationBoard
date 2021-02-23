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

from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.util.Plugin import Plugin
from backend.action.ActionSendMessagePowerAlarm import ActionSendMessagePowerAlarm, _PowerAlarmMessage
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.event.UnhandledEvent import UnhandledEvent

class Test_ActionSendMessagePowerAlarm:

    EVENT = "EVENT"
    EVENT_DETAILS = "E_DETAILS"
    LOCATION = "LOCATION"
    LOCATION_DETAILS = "L_DETAILS"
    COMMENT = "COMMENT"
    RAW_CONTENT = "RAW_CONTENT"

    LOCATION_LATITUDE = 13.02
    LOCATION_LONGITUDE = 21.10

    SETTING_KEY = "KEY"
    SETTING_VALUE = "VALUE"

    def setup_class(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        self.settings = Settings(settingsFilename, appInfo.path)

        section = ActionSendMessagePowerAlarm.PLUGIN_TYPE + Plugin.NAME_SEPARATOR + "send_poweralarm"
        self.settings.setString(section, "api_key", "NO_API_KEY")

        self.settings.setString(section, "api_group_nodetails", "NODETAILS")
        self.settings.setString(section, "api_group_reduced", "REDUCED")
        self.settings.setString(section, "api_group_full", "FULL")
        self.settings.setString(section, "api_group_tablet", "TABLET")
        self.settings.setString(section, "api_group_binary", "BINARY")
        self.settings.setString(section, "api_group_admin", "ADMIN")

        self.settings.setBoolean(section, "send_invalid", True)

        self.settings.setBoolean(section, "admin_send_setting", True)
        self.settings.setBoolean(section, "admin_send_unhandled", True)
        self.settings.setBoolean(section, "admin_send_invalid", False)

        self.settings.setString(section, "alarm_message", "TEST_ALARM")

        self.action = ActionSendMessagePowerAlarm("", self.settings, test=True)

    def test_send_alarm_event_valid(self) -> None:
        alarmEvent = self.__createAlarmEvent(flags=AlarmEvent.FLAGS_VALID)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=True)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=True)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(msg.isEmpty())

    def test_send_alarm_event_invalid(self) -> None:
        alarmEvent = self.__createAlarmEvent(flags=AlarmEvent.FLAGS_INVALID)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(not msg.isEmpty())
        self.__checkMetadata(msg, location=False)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.EVENT_DETAILS)
        self.__notContainsInfo(msg, Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS)
        self.__containsInfo(msg, Test_ActionSendMessagePowerAlarm.RAW_CONTENT)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(msg.isEmpty())

    def test_send_alarm_event_binary(self) -> None:
        alarmEvent = self.__createAlarmEvent(flags=AlarmEvent.FLAGS_BINARY)

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(not msg.isEmpty())

        msg = self.action.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(msg.isEmpty())

    def test_send_setting_event_valid(self) -> None:
        settingEvent = self.__createSettingEvent(flags=SettingEvent.FLAGS_VALID)

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(not msg.isEmpty())

    def test_send_setting_event_invalid(self) -> None:
        settingEvent = self.__createSettingEvent(flags=SettingEvent.FLAGS_INVALID)

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(not msg.isEmpty())

    def test_send_unhandled_event_ignored_sender(self) -> None:
        unhandledEvent = UnhandledEvent(cause=UnhandledEvent.CAUSE_IGNORED_SENDER)

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(not msg.isEmpty())

    def test_send_unhandled_event_unparsable_message(self) -> None:
        unhandledEvent = UnhandledEvent(cause=UnhandledEvent.CAUSE_UNPARSABLE_MESSAGE)

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)
        assert(msg.isEmpty())

        msg = self.action.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
        assert(not msg.isEmpty())

    def __createSettingEvent(self, flags: str) -> SettingEvent:
        settingEvent = SettingEvent()
        settingEvent.key = Test_ActionSendMessagePowerAlarm.SETTING_KEY
        settingEvent.value = Test_ActionSendMessagePowerAlarm.SETTING_VALUE
        settingEvent.flags = flags
        return settingEvent

    def __createAlarmEvent(self, flags: str) -> AlarmEvent:
        alarmEvent = AlarmEvent()
        alarmEvent.event = Test_ActionSendMessagePowerAlarm.EVENT
        alarmEvent.eventDetails = Test_ActionSendMessagePowerAlarm.EVENT_DETAILS
        alarmEvent.location = Test_ActionSendMessagePowerAlarm.LOCATION
        alarmEvent.locationDetails = Test_ActionSendMessagePowerAlarm.LOCATION_DETAILS
        alarmEvent.comment = Test_ActionSendMessagePowerAlarm.COMMENT
        alarmEvent.raw = Test_ActionSendMessagePowerAlarm.RAW_CONTENT
        alarmEvent.locationLatitude = Test_ActionSendMessagePowerAlarm.LOCATION_LATITUDE
        alarmEvent.locationLongitude = Test_ActionSendMessagePowerAlarm.LOCATION_LONGITUDE
        alarmEvent.flags = flags
        return alarmEvent

    def __checkMetadata(self, message: _PowerAlarmMessage, location: bool = False) -> None:
        if location:
            assert(message.hasLocation())
        else:
            assert(not message.hasLocation())

    def __containsInfo(self, message: _PowerAlarmMessage, info: str) -> None:
        assert((info in message.text) or (info in message.details))

    def __notContainsInfo(self, message: _PowerAlarmMessage, info: str) -> None:
        assert((not info in message.text) and (not info in message.details))
