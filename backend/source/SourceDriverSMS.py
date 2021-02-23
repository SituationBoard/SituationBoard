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

from typing import Optional

import gammu #pylint: disable=import-error

from backend.source.SourceDriver import SourceDriver, SourceState
from backend.source.MessageParser import MessageParser
from backend.event.SourceEvent import SourceEvent
from backend.event.UnhandledEvent import UnhandledEvent
from backend.util.Settings import Settings

class SourceDriverSMS(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings, parser: MessageParser) -> None:
        super().__init__("sms", instanceName, settings, parser)
        self.__gammuConfig = self.getSettingFilename("gammu_config", "/etc/gammu-smsdrc")
        self.__allowlist   = self.getSettingList("allowlist", [])
        self.__denylist   = self.getSettingList("denylist", [])
        self.__lastEvent: Optional[SourceEvent] = None

        self.__gsm = gammu.StateMachine()
        try:
            self.__gsm.ReadConfig(Filename=self.__gammuConfig)
            self.__gsm.Init()
        except gammu.ERR_CANTOPENFILE:
            self.fatal("Config file not found")
        except gammu.ERR_DEVICENOTEXIST:
            self.fatal("Modem device is not available")
        except Exception as e:
            self.fatal("Could not initialize SMS driver", e)

    def retrieveEvent(self) -> Optional[SourceEvent]:
        if self.__gsm is None:
            return None
        if self.parser is None:
            return None

        start = True
        cursms = None
        sms = []

        # self.dbgPrint("Searching for new SMS")

        status = self.__gsm.GetSMSStatus()

        remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

        try:
            while remain > 0:
                if start:
                    cursms = self.__gsm.GetNextSMS(Start=True, Folder=0)
                    start = False
                elif cursms is not None:
                    cursms = self.__gsm.GetNextSMS(Location=cursms[0]['Location'], Folder=0) #pylint: disable=unsubscriptable-object
                else:
                    self.error("Failed to read further messages")
                    break
                remain = remain - len(cursms)
                sms.append(cursms)
        except gammu.ERR_EMPTY:
            # This error is raised when we've reached last entry
            # It can happen when reported status does not match real counts
            self.error("Failed to read all messages")

        # while True:
        #     try:
        #         if start:
        #             cursms = self.__gsm.GetNextSMS(Start = True, Folder = 0)
        #             start = False
        #         else:
        #             cursms = self.__gsm.GetNextSMS(Location = cursms[0]['Location'], Folder = 0)
        #
        #         sms.append(cursms)
        #     except gammu.ERR_EMPTY:
        #         break

        if start:
            return None

        data = gammu.LinkSMS(sms)

        rawText   = ""
        sender    = ""
        timeStamp = ""
        foundMessage = False
        locs = []

        for x in data:
            v = gammu.DecodeSMS(x)

            m = x[0]

            # all parts of multipart SMS received ?
            if m['UDH']['AllParts'] > len(x):
                continue

            timeStamp    = str(m['DateTime'])
            sender       = m['Number']

            for m in x:
                locs.append(m['Location'])

            if v is None:
                rawText += m['Text'] # .encode('utf-8')
            else:
                for e in v['Entries']:
                    if e['Buffer'] is not None:
                        rawText += e['Buffer'] # .encode('utf-8')

            foundMessage = True
            break

        if not foundMessage:
            return None

        for loc in locs:
            self.__gsm.DeleteSMS(Location = loc, Folder = 0)

        self.clrPrint("Received message")

        self.dbgPrint("Received SMS from " + sender + " (timestamp " + timeStamp + ")")
        self.dbgPrint(rawText)

        sourceEvent = SourceEvent()
        sourceEvent.source = SourceEvent.SOURCE_SMS
        sourceEvent.timestamp = timeStamp
        sourceEvent.sender = sender
        sourceEvent.raw = rawText

        if not SourceDriver.isSenderAllowed(allowlist=self.__allowlist, denylist=self.__denylist, sender=sender):
            self.error("Received unhandled message (ignored sender)")
            return UnhandledEvent.fromSourceEvent(sourceEvent, UnhandledEvent.CAUSE_IGNORED_SENDER)

        parsedSourceEvent = self.parser.parseMessage(sourceEvent, self.__lastEvent)

        if parsedSourceEvent is not None:
            self.__lastEvent = parsedSourceEvent

        return parsedSourceEvent

    def getSourceState(self) -> SourceState:
        if self.__gsm is None:
            return SourceState.ERROR
        if self.parser is None:
            return SourceState.ERROR

        # networkSignal = self.__gsm.GetSignalQuality()
        networkInfo = self.__gsm.GetNetworkInfo()

        # self.dbgPrint(networkSignal)
        # self.dbgPrint(networkInfo)

        if networkInfo["NetworkCode"] != "":
            return SourceState.OK

        return SourceState.ERROR
