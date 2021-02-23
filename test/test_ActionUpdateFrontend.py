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

from typing import Tuple, Any

from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.api.WebSocket import WebSocket
from backend.data.Database import Database
from backend.action.ActionUpdateFrontend import ActionUpdateFrontend
from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.util.PluginManager import PluginManager

class Test_ActionUpdateFrontend:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")
        databaseFilename = os.path.join(appInfo.path, ".temp/situationboard.sqlite")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        self.database = Database(databaseFilename, reset = True)

        settings = Settings(settingsFilename, appInfo.path)
        settings.setFrontendHeader("header")
        settings.setFrontendNews("news")

        displayPowerManager = DisplayPowerManager(settings)

        self.webSocket = WebSocket(appInfo, settings, self.database)

        pluginManager = PluginManager(settings, self.database, self.webSocket, displayPowerManager)

        self.webSocket.init(pluginManager)

        appClient = self.webSocket.app_test_client()
        self.socketClient = self.webSocket.socket_test_client(appClient)

        self.action = ActionUpdateFrontend("", settings, self.webSocket)

    def teardown_class(self) -> None:
        self.database.commitAndClose()

    def test_handle_event_alarm(self) -> None:
        alarmEvent = AlarmEvent(1302)
        self.action.handleEvent(alarmEvent)
        (event, args) = self.__getReceived()
        assert(event == "alarm_event")
        assert(args is not None)
        assert(args['eventID'] == 1302)

    def test_handle_event_setting_header(self) -> None:
        settingEvent = SettingEvent()
        settingEvent.key = "header"
        settingEvent.value = "new header"
        self.action.handleEvent(settingEvent)
        (event, args) = self.__getReceived()
        assert(event == "header")
        assert(args is not None)
        assert(args['header'] == "new header")

    def test_handle_event_setting_news(self) -> None:
        settingEvent = SettingEvent()
        settingEvent.key = "news"
        settingEvent.value = "new news"
        self.action.handleEvent(settingEvent)
        (event, args) = self.__getReceived()
        assert(event == "news")
        assert(args is not None)
        assert(args['news'] == "new news")

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
