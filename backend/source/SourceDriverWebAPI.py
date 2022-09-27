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
import urllib
import queue

from typing import Optional

from flask import Response, request

from backend.source.MessageParser import MessageParser
from backend.source.SourceDriver import SourceDriver, SourceState
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.util.Settings import Settings
from backend.api.WebSocket import WebSocket

# send alarm with:
# curl -X POST http://192.168.0.28:5000/v1/alarm_api -H "X-API-KEY: xyzabc-123" -d @test/edi.json

#TODO: add curl <API> <DATA(-FILE)> feature to sbctl

#TODO: add documentation for plugin

class SourceDriverWebAPI(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings, webSocket: WebSocket, messageParser: MessageParser) -> None:
        super().__init__("webapi", instanceName, settings, multipleInstances=True)
        self.__webSocket = webSocket
        self.__messageParser = messageParser
        self.__apiURL = self.getSettingString("api_url", "/v1/alarm_api")
        self.__apiKey = self.getSettingString("api_key", "") #TODO: support multiple API keys ?!?
        self.__stateURL = self.getSettingString("state_url", "https://google.com")
        self.__stateTimeout = self.getSettingInt("state_timeout", 5)
        self.__webSocket.register_url_handler(self.__apiURL, "alarm_api", self.__handleEvent, methods=["POST"])
        if TYPE_CHECKING:
            self.__eventQueue: queue.Queue[SourceEvent] = queue.Queue()
        else:
            self.__eventQueue: queue.Queue = queue.Queue()
        self.__lastEvent: Optional[SourceEvent] = None

    def __handleEvent(self) -> Response:
        auth = request.headers.get("X-Api-Key")
        self.print(f"auth: {auth}")
        self.print(f"apiKey: {self.__apiKey}")

        if self.__apiKey == auth: #TODO: check what happens when no key is configured and/or provided
            moment = datetime.datetime.now()
            ts = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)

            sourceEvent = SourceEvent()
            sourceEvent.source    = SourceEvent.SOURCE_WEBAPI
            sourceEvent.sender    = request.remote_addr + "/" + auth
            sourceEvent.raw       = request.get_data().decode("utf-8")
            sourceEvent.timestamp = ts

            #TODO: parser here to determine whether we could actually parse the message ?!?

            self.print("put event")
            self.__eventQueue.put(sourceEvent)

            return { 'result': 'ok' }

        return { 'result': 'error' }

    def __checkInternet(self) -> bool:
        try:
            with urllib.request.urlopen(self.__stateURL, timeout=self.__stateTimeout):
                return True
        except urllib.error.URLError:
            return False

    def retrieveEvent(self) -> Optional[SourceEvent]:
        try:
            sourceEvent = self.__eventQueue.get_nowait()
            self.print(f"retrieved event: {sourceEvent}")

            parsedSourceEvent = self.__messageParser.parseMessage(sourceEvent, self.__lastEvent)

            if parsedSourceEvent is not None:
                self.__lastEvent = parsedSourceEvent

            return parsedSourceEvent
        except queue.Empty:
            return None

    def getSourceState(self) -> SourceState:
        sourceState = SourceState.ERROR

        if self.__checkInternet():
            sourceState = SourceState.OK

        self.logSourceStateChange(sourceState)

        return sourceState
