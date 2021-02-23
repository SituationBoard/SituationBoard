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

from typing import Tuple, Any, Dict, Optional

from backend.api.WebSocket import WebSocket
from backend.data.Database import Database
from backend.source.SourceDriver import SourceState
from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.util.PluginManager import PluginManager
from backend.event.AlarmEvent import AlarmEvent

class Test_WebSocket:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        self.appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(self.appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(self.appInfo.path, ".temp/situationboard.conf")
        databaseFilename = os.path.join(self.appInfo.path, ".temp/situationboard.sqlite")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        self.database = Database(databaseFilename, reset = True)

        settings = Settings(settingsFilename, self.appInfo.path)
        settings.setFrontendHeader("header")
        settings.setFrontendNews("news")
        settings.setBoolean(Settings.SECTION_BACKEND, "web_api", True)

        displayPowerManager = DisplayPowerManager(settings)

        self.webSocket = WebSocket(self.appInfo, settings, self.database)

        pluginManager = PluginManager(settings, self.database, self.webSocket, displayPowerManager)

        self.webSocket.init(pluginManager)

        self.appClient = self.webSocket.app_test_client()
        self.socketClient = self.webSocket.socket_test_client(self.appClient)

    def teardown_class(self) -> None:
        self.database.commitAndClose()

    def test_get_last_alarm_events(self) -> None:
        self.__emit("get_last_alarm_events", {'count': 10})
        (event, args) = self.__getReceived()
        assert(event == "last_alarm_events")
        assert(args['total_events'] == 0)
        assert(args['alarm_events'] == "[]")

    def test_get_stats(self) -> None:
        self.__emit("get_stats")
        (event, args) = self.__getReceived()
        assert(event == "stats")
        assert(args is not None)
        assert(args['total'] == 0)
        assert(args['year'] == 0)
        assert(args['month'] == 0)
        assert(args['today'] == 0)

    def test_get_header(self) -> None:
        self.__emit("get_header")
        (event, args) = self.__getReceived()
        assert(event == "header")
        assert(args is not None)
        assert(args['header'] == "header")

    def test_get_news(self) -> None:
        self.__emit("get_news")
        (event, args) = self.__getReceived()
        assert(event == "news")
        assert(args is not None)
        assert(args['news'] == "news")

    def test_get_state(self) -> None:
        self.__emit("get_state")
        (event, args) = self.__getReceived()
        assert(event == "state")
        assert(args is not None)
        assert(args['version'] == self.appInfo.version)
        assert(args['start_timestamp'] > 0)
        assert(args['source_state'] == SourceState.OK)

    def test_broadcast_alarm_event(self) -> None:
        alarmEvent = AlarmEvent(1302)
        self.webSocket.broadcastAlarmEvent(alarmEvent)
        (event, args) = self.__getReceived()
        assert(event == "alarm_event")
        assert(args is not None)
        assert(args['eventID'] == 1302)

    def test_broadcast_header(self) -> None:
        self.webSocket.broadcastHeader("TEST\nHEADER")
        (event, args) = self.__getReceived()
        assert(event == "header")
        assert(args is not None)
        assert(args['header'] == "TEST\nHEADER")

    def test_broadcast_news(self) -> None:
        self.webSocket.broadcastNews("TEST\nNEWS")
        (event, args) = self.__getReceived()
        assert(event == "news")
        assert(args is not None)
        assert(args['news'] == "TEST\nNEWS")

    def test_broadcast_database_changed(self) -> None:
        self.webSocket.broadcastDatabaseChanged()
        (event, _) = self.__getReceived()
        assert(event == "database_changed")

    def test_broadcast_calendar_changed(self) -> None:
        self.webSocket.broadcastCalendarChanged()
        (event, _) = self.__getReceived()
        assert (event == "calendar_changed")

    def test_static(self) -> None:
        response = self.appClient.get('/css/situationboard.css')
        assert(response.status_code == 200)

    def test_index(self) -> None:
        response = self.appClient.get('/')
        assert(response.status_code == 200)

    def test_javascript_frontend(self) -> None:
        response = self.appClient.get('/js/situationboard.js')
        assert(response.status_code == 200)

    def test_javascript_settings(self) -> None:
        response = self.appClient.get('/js/frontend/util/settings.js')
        assert(response.status_code == 200)

    def test_api_stats(self) -> None:
        response = self.appClient.get('/api/v1/stats')
        assert(response.status_code == 200)
        assert(response.json['result'] == "ok")
        stats = response.json['stats']
        assert(stats['total'] == 0)
        assert(stats['year'] == 0)
        assert(stats['month'] == 0)
        assert(stats['today'] == 0)

    def test_api_state(self) -> None:
        response = self.appClient.get('/api/v1/state')
        assert(response.status_code == 200)
        assert(response.json['result'] == "ok")
        state = response.json['state']
        assert(state['version'] == self.appInfo.version)
        assert(state['start_timestamp'] > 0)
        assert(state['source_state'] == SourceState.OK)

    def __emit(self, event: str, args: Optional[Dict[str, Any]] = None) -> None:
        if args is not None:
            self.socketClient.emit(event, args, namespace=WebSocket.NS)
        else:
            self.socketClient.emit(event, namespace=WebSocket.NS)

    def __getReceived(self) -> Tuple[Any, Any]:
        response = self.socketClient.get_received(WebSocket.NS)
        assert(len(response) == 1)
        result = response[0]
        event = result['name']
        argsList = result['args']
        asgsListLen = len(argsList)
        assert(asgsListLen <= 1)
        if asgsListLen == 1:
            args = argsList[0]
            return (event, args)

        return (event, None)
