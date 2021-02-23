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

import json
import time

import urllib.parse as URLParse
import http.client as HTTPClient

from typing import List, Optional

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.event.UnhandledEvent import UnhandledEvent

class _PowerAlarmMessage:

    def __init__(self, alarmText: str = ""):
        self.text = alarmText
        self.details = ""
        self.locationLongitude = 0.0
        self.locationLatitude = 0.0
        self.timestamp = 0.0

    def isEmpty(self) -> bool:
        return (self.text == "" and self.details == "")

    def hasDetails(self) -> bool:
        return self.details != ""

    def hasLocation(self) -> bool:
        return (self.locationLatitude != 0.0 or self.locationLongitude != 0.0)

    def isIdentical(self, message: "_PowerAlarmMessage") -> bool:
        return (self.text == message.text
            and self.details == message.details
            and self.locationLongitude == message.locationLongitude
            and self.locationLatitude == message.locationLatitude)

class ActionSendMessagePowerAlarm(Action):

    API_URL = "www.poweralarm.de"
    API_REQUEST = "/api/custom/?apikey={VAPIKEY}&action={VACTION}&kuerzel={VGROUP}&text={VMESSAGE}"
    API_REQUEST_ADDON_DETAILS = "&zusatz={VDETAILS}"
    API_REQUEST_ADDON_LOCATION = "&lat={VLAT}&long={VLONG}"
    API_ACTION = "triggergroupalarm"

    API_GROUP_NODETAILS = 0
    API_GROUP_REDUCED   = 1
    API_GROUP_FULL      = 2
    API_GROUP_TABLET    = 3
    API_GROUP_BINARY    = 4
    API_GROUP_ADMIN     = 5
    API_GROUP_MAX       = 6

    def __init__(self, instanceName: str, settings: Settings, test: bool = False):
        super().__init__("send_poweralarm", instanceName, settings)
        self.__test = test

        self.__apiKey                = self.getSettingString("api_key", "")
        self.__timeout               = self.getSettingInt("timeout", 5)
        self.__alarmMessage          = self.getSettingString("alarm_message", "Alarm")
        self.__deduplicationDuration = self.getSettingInt("deduplication_duration", 60)
        self.__sendInvalid           = self.getSettingBoolean("send_invalid", True)
        self.__adminSendSetting      = self.getSettingBoolean("admin_send_setting", False)
        self.__adminSendUnhandled    = self.getSettingBoolean("admin_send_unhandled", True)
        self.__adminSendInvalid      = self.getSettingBoolean("admin_send_invalid", False)

        self.__lastMessage: List[Optional[_PowerAlarmMessage]] = [None] * ActionSendMessagePowerAlarm.API_GROUP_MAX

        self.__apiGroups = [""] * ActionSendMessagePowerAlarm.API_GROUP_MAX
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_NODETAILS] = self.getSettingString("api_group_nodetails", "")
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_REDUCED]   = self.getSettingString("api_group_reduced", "")
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_FULL]      = self.getSettingString("api_group_full", "")
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_TABLET]    = self.getSettingString("api_group_tablet", "")
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_BINARY]    = self.getSettingString("api_group_binary", "")
        self.__apiGroups[ActionSendMessagePowerAlarm.API_GROUP_ADMIN]     = self.getSettingString("api_group_admin", "")

        if self.__apiKey == "":
            self.fatal("No API key specified in configuration")

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            alarmEvent = sourceEvent

            if alarmEvent.valid:
                self.dbgPrint("Handling valid alarm event")
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
            elif alarmEvent.invalid:
                self.dbgPrint("Handling invalid alarm event")
                # depending on the configuration (and group type) a raw or fallback message might be sent
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_NODETAILS)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_REDUCED)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_FULL)
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_TABLET)
                # depending on the configuration invalid alarm events might also be sent to the admin group
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)
            elif alarmEvent.binary:
                self.dbgPrint("Handling binary alarm event")
                self.sendAlarmEvent(alarmEvent, ActionSendMessagePowerAlarm.API_GROUP_BINARY)

        elif isinstance(sourceEvent, SettingEvent):
            settingEvent = sourceEvent

            self.dbgPrint("Handling setting event")
            self.sendSettingEvent(settingEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)

        elif isinstance(sourceEvent, UnhandledEvent):
            unhandledEvent = sourceEvent

            self.dbgPrint("Handling unhandled event")
            self.sendUnhandledEvent(unhandledEvent, ActionSendMessagePowerAlarm.API_GROUP_ADMIN)

    def sendAlarmEvent(self, alarmEvent: AlarmEvent, apiGroupID: int) -> _PowerAlarmMessage:
        message = _PowerAlarmMessage()

        if apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_ADMIN:
            if not alarmEvent.invalid or not self.__adminSendInvalid:
                return message # ignore all alarm events except invalid alarm events if adminSendInvalid is True
        else:
            if alarmEvent.invalid and not self.__sendInvalid:
                return message # ignore invalid alarm events except if sendInvalid is true

        if apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_NODETAILS:
            if alarmEvent.valid or alarmEvent.invalid:
                message.text = self.__alarmMessage + "\n"
                message.text += alarmEvent.alarmTimestamp

        elif apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_REDUCED:
            if alarmEvent.invalid:
                message.text = self.__alarmMessage + "\n"
                message.text += alarmEvent.alarmTimestamp
            elif alarmEvent.valid:
                message.text = alarmEvent.event + "\n"
                message.text += alarmEvent.eventDetails + "\n"
                message.text += alarmEvent.location + "\n"
                message.text += alarmEvent.alarmTimestamp

        elif apiGroupID in [ActionSendMessagePowerAlarm.API_GROUP_FULL,
                            ActionSendMessagePowerAlarm.API_GROUP_TABLET,
                            ActionSendMessagePowerAlarm.API_GROUP_ADMIN]:
            if alarmEvent.invalid:
                message.text = alarmEvent.raw + "\n"
                # message.text += alarmEvent.sender + "\n"
                message.text += alarmEvent.alarmTimestamp
            elif alarmEvent.valid:
                message.text = alarmEvent.event + "\n"
                message.text += alarmEvent.eventDetails + "\n"
                # add the following details also to the regular messageText (to make sure it is also visible in SMS)
                message.text += alarmEvent.location + "\n"
                message.text += alarmEvent.locationDetails + "\n"
                message.text += "\n"
                message.text += alarmEvent.comment + "\n"
                message.text += "\n"
                message.text += alarmEvent.alarmTimestamp

                # message.details = alarmEvent.location + "\n"
                # message.details += alarmEvent.locationDetails + "\n"
                # message.details += "\n"
                # message.details += alarmEvent.comment + "\n"
                # message.details += "\n"
                # message.details += alarmEvent.alarmTimestamp

                message.locationLatitude = alarmEvent.locationLatitude
                message.locationLongitude = alarmEvent.locationLongitude

        elif apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_BINARY:
            if alarmEvent.binary:
                eventText = alarmEvent.raw if alarmEvent.raw != "" else self.__alarmMessage
                message.text = eventText + "\n"
                message.text += alarmEvent.alarmTimestamp
        else:
            self.error("Invalid group ID for source event type")

        self.sentToPowerAlarm(apiGroupID, message)
        return message

    def sendSettingEvent(self, settingEvent: SettingEvent, apiGroupID: int) -> _PowerAlarmMessage:
        message = _PowerAlarmMessage()

        if not self.__adminSendSetting:
            return message

        if apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_ADMIN:
            message.text = f"{settingEvent}\n"
            # add the following details also to the regular messageText (to make sure it is also visible in SMS)
            message.text += settingEvent.sender + "\n"
            message.text += settingEvent.timestamp + "\n"

            # message.details = settingEvent.sender + "\n"
            # message.details += settingEvent.timestamp + "\n"
        else:
            self.error("Invalid group ID for source event type")

        self.sentToPowerAlarm(apiGroupID, message)
        return message

    def sendUnhandledEvent(self, unhandledEvent: UnhandledEvent, apiGroupID: int) -> _PowerAlarmMessage:
        message = _PowerAlarmMessage()

        if not self.__adminSendUnhandled:
            return message

        if apiGroupID == ActionSendMessagePowerAlarm.API_GROUP_ADMIN:
            message.text = f"{unhandledEvent}\n"
            # add the following details also to the regular messageText (to make sure it is also visible in SMS)
            message.text += unhandledEvent.raw + "\n"
            message.text += unhandledEvent.sender + "\n"
            message.text += unhandledEvent.timestamp + "\n"

            # message.details = unhandledEvent.raw + "\n"
            # message.details += unhandledEvent.sender + "\n"
            # message.details += unhandledEvent.timestamp + "\n"
        else:
            self.error("Invalid group ID for source event type")

        self.sentToPowerAlarm(apiGroupID, message)
        return message

    def sentToPowerAlarm(self, apiGroupID: int, message: _PowerAlarmMessage) -> None:
        if self.__test:
            return

        apiGroup = ""
        if 0 <= apiGroupID < len(self.__apiGroups):
            apiGroup = self.__apiGroups[apiGroupID]
        else:
            # Invalid API group ID
            return

        if apiGroup == "":
            # API group not in use
            return

        if message.isEmpty():
            return

        if self.__deduplicationDuration > 0:
            # Check for message duplication
            lastMessage = self.__lastMessage[apiGroupID]
            if lastMessage is not None:
                # There was a previous message for this group
                secondsPassed = time.time() - lastMessage.timestamp
                if secondsPassed < self.__deduplicationDuration:
                    # It was not sent too long ago
                    if message.isIdentical(lastMessage):
                        # Exactly the same message already sent to this group not too long ago -> ignore new message
                        return

        self.print(f"Sending message to group {apiGroup}")

        self.dbgPrint(f"Message:\n{message.text}")
        completeRequest = ActionSendMessagePowerAlarm.API_REQUEST.format(
            VAPIKEY=URLParse.quote(self.__apiKey, ""),
            VACTION=URLParse.quote(ActionSendMessagePowerAlarm.API_ACTION, ""),
            VGROUP=URLParse.quote(apiGroup, ""),
            VMESSAGE=URLParse.quote(message.text, ""))

        if message.hasDetails():
            self.dbgPrint(f"Details:\n{message.details}")
            completeRequest += ActionSendMessagePowerAlarm.API_REQUEST_ADDON_DETAILS.format(
                VDETAILS=URLParse.quote(message.details, ""))

        if message.hasLocation():
            self.dbgPrint(f"Latitude/Longitude:\n{message.locationLatitude}/{message.locationLongitude}")
            completeRequest += ActionSendMessagePowerAlarm.API_REQUEST_ADDON_LOCATION.format(
                VLAT=message.locationLatitude, VLONG=message.locationLongitude)

        try:
            connection = HTTPClient.HTTPSConnection(ActionSendMessagePowerAlarm.API_URL, 443, timeout=self.__timeout)
            connection.connect()

            self.dbgPrint(f"API request:\n{completeRequest}")

            connection.request('GET', completeRequest)
            response = connection.getresponse().read().decode("utf-8")
            try:
                result = json.loads(response)
                self.dbgPrint(f"API response:\n{json.dumps(result)}")
            except Exception:
                self.dbgPrint(f"API response:\n{response}")

            message.timestamp = time.time()
            self.__lastMessage[apiGroupID] = message

        except Exception as e:
            self.error(f"Failed to send message ({e})")
