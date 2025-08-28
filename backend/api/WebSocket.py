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
import errno

from typing import Optional, Callable, Dict, Any

from flask import Flask, Response, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit

from backend.util.AppInfo import AppInfo
from backend.util.Module import Module
from backend.util.Settings import Settings
from backend.util.PluginManager import PluginManager
from backend.data.Database import Database, DatabaseTimespan
from backend.source.SourceDriver import SourceState
from backend.event.AlarmEvent import AlarmEvent

class WebSocket(Module):
    """The WebSocket class is responsible for handling the websocket connection between frontend and backend.
    In addition, it also serves the web frontend and provides the web client with all the static files."""

    # Set this variable to "threading", "eventlet" or "gevent" to test the
    # different async modes, or leave it set to None for the application to choose
    # the best option based on installed packages.
    SOCKETIO_ASYNC_MODE = None  # "gevent"

    NS = '/situationboard'  # namespace
    FF = 'frontend/'     # frontend folder

    MIME_JS = 'application/javascript'

    def __init__(self, appInfo: AppInfo, settings: Settings, database: Database):
        super().__init__("websocket", settings)
        self.appInfo = appInfo
        self.settings = settings
        self.database = database
        self.pluginManager: Optional[PluginManager] = None

        self.clientCount = 0

        self.app = Flask(self.appInfo.name, static_url_path='', static_folder=WebSocket.FF, template_folder=WebSocket.FF)
        self.app.config['SECRET_KEY'] = 'secret!'

        self.socketio = SocketIO(self.app, async_mode=WebSocket.SOCKETIO_ASYNC_MODE)
        self.btask: Any = None

    def init(self, pluginManager: PluginManager) -> None:
        self.pluginManager = pluginManager

        # register flask handlers
        self.app.after_request(self.__app_add_header)
        self.app.add_url_rule('/<path:path>',                  'send_static',          self.__app_send_static)
        self.app.add_url_rule('/',                             'index',                self.__app_index)
        self.app.add_url_rule('/js/situationboard.js',         'javascript_frontend',  self.__app_javascript_frontend)
        self.app.add_url_rule('/js/frontend/util/settings.js', 'javascript_settings',  self.__app_javascript_settings)

        # register web api (if configured)
        if self.settings.getBackendWebAPI():
            self.app.add_url_rule('/api/v1/stats',             'api_stats',            self.__api_stats)
            self.app.add_url_rule('/api/v1/state',             'api_state',            self.__api_state)

        # register socket io handlers
        self.socketio.on_event("connect", self.__socket_connect, WebSocket.NS)
        self.socketio.on_event("disconnect", self.__socket_disconnect, WebSocket.NS)
        self.socketio.on_event("get_last_alarm_events", self.__socket_get_last_alarm_events, WebSocket.NS)
        self.socketio.on_event("get_stats", self.__socket_get_stats, WebSocket.NS)
        self.socketio.on_event("get_header", self.__socket_get_header, WebSocket.NS)
        self.socketio.on_event("get_news", self.__socket_get_news, WebSocket.NS)
        self.socketio.on_event("get_state", self.__socket_get_state, WebSocket.NS)

    def sleep(self, duration: int) -> None:
        self.socketio.sleep(duration)

    def start_background_task(self, target: Callable[[], None]) -> None:
        self.btask = self.socketio.start_background_task(target=target)

    def __broadcast(self, event: str, data: Dict[str, Any]) -> None:
        self.socketio.emit(event, data, namespace=WebSocket.NS)

    def run(self) -> None:
        port = self.settings.getBackendServerPort()

        self.clrPrint(f"Listening on port {port}")

        try:
            self.socketio.run(self.app,
                     host=self.settings.getBackendServerHost(),
                     port=self.settings.getBackendServerPort(),
                     debug=self.settings.getBackendDebug(),
                     use_reloader=self.settings.getBackendReloader())
        except OSError as ose:
            if ose.errno == errno.EADDRINUSE:
                self.fatal(f"Port {port} is already in use")
            else:
                self.fatal("Unhandled OS exception", ose)
        except Exception as e:
            self.fatal("Unhandled exception", e)

    def app_test_client(self) -> Any:
        return self.app.test_client()

    def socket_test_client(self, appTestClient: Any = None) -> Any:
        return self.socketio.test_client(self.app, WebSocket.NS, flask_test_client=appTestClient)

    def __app_add_header(self, response: Any) -> Any:
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response

    def __app_send_static(self, path: Any) -> Any:
        self.dbgPrint(f"Sending static file ({path})")
        return send_from_directory('.', path)

    def __app_javascript_frontend(self) -> Response:
        template = "js/situationboard.js"
        self.dbgPrint(f"Rendering template ({template})")
        data = render_template(template,
                     tVersion=str(self.appInfo.version),
                     tStartTimestamp=str(self.appInfo.start))
        return Response(data, mimetype=WebSocket.MIME_JS)

    def __app_javascript_settings(self) -> Response:
        template = "js/frontend/util/settings.js"
        self.dbgPrint(f"Rendering template ({template})")
        data = render_template(template,
                     tDebug=str(self.settings.getFrontendDebug()).lower(),
                     tLanguage=str(self.settings.getFrontendLanguage()),
                     tAlarmDuration=str(self.settings.getFrontendAlarmDuration()),
                     tAlarmShowMaps=str(self.settings.getFrontendAlarmShowMaps()),
                     tCalendarURL=self.settings.getFrontendCalendarURL(),
                     tCalendarUpdateDuration=str(self.settings.getFrontendCalendarUpdateDuration()),
                     tStandbyShowStatistics=str(self.settings.getFrontendStandbyShowStatistics()).lower(),
                     tStandbyShowClock=str(self.settings.getFrontendStandbyShowClock()).lower(),
                     tPageReloadDuration=str(self.settings.getFrontendPageReloadDuration()),
                     tMapService=str(self.settings.getFrontendMapService()),
                     tMapAPIKey=str(self.settings.getFrontendMapAPIKey()),
                     tMapZoom=str(self.settings.getFrontendMapZoom()),
                     tMapType=str(self.settings.getFrontendMapType()),
                     tMapEmergencyLayer=str(self.settings.getFrontendMapEmergencyLayer()),
                     tMapHomeLatitude=str(self.settings.getFrontendMapHomeLatitude()),
                     tMapHomeLongitude=str(self.settings.getFrontendMapHomeLongitude()),
                     tMapSearchLocation=str(self.settings.getFrontendMapSearchLocation()).lower(),
                     tShowSplashScreen=str(self.settings.getFrontendShowSplashScreen()).lower())
        return Response(data, mimetype=WebSocket.MIME_JS)

    def __app_index(self) -> Response:
        template = "index.html"
        self.dbgPrint(f"Rendering template ({template})")
        data = render_template(template)
        return Response(data)

    def __api_stats(self) -> Dict[str, Any]:
        self.dbgPrint("Answering stats Web API request")
        return { 'result': 'ok', 'stats': self.__get_stats_dict() }

    def __api_state(self) -> Dict[str, Any]:
        self.dbgPrint("Answering state Web API request")
        return { 'result': 'ok', 'state': self.__get_state_dict() }

    def __socket_connect(self) -> None:
        session["ClientID"] = self.clientCount
        self.clientCount += 1
        self.print(f"Client {session['ClientID']} connected ({request.remote_addr}, {request.sid})")

    def __socket_disconnect(self) -> None:
        self.print(f"Client {session['ClientID']} disconnected ({request.remote_addr}, {request.sid})")

    def __socket_get_last_alarm_events(self, message: Any) -> None:
        self.dbgPrint(f"Answering get_last_alarm_events (Client {session['ClientID']})")

        count = -1
        if isinstance(message, dict) and 'count' in message:
            if isinstance(message['count'], int):
                count = message['count']

        totalEvents = self.database.getEventCount(textOnly = True)
        count = count if count > 0 else totalEvents
        alarmEvents = self.database.getLastEvents(count, textOnly = True)

        emit('last_alarm_events', {
            'total_events': totalEvents,
            'alarm_events': json.dumps([alarmEvent.toJSON() for alarmEvent in alarmEvents])
        })

    def __socket_get_stats(self) -> None:
        self.dbgPrint(f"Answering get_stats (Client {session['ClientID']})")
        emit('stats', self.__get_stats_dict())

    def __socket_get_state(self) -> None:
        # self.dbgPrint(f"Answering get_state (Client {session['ClientID']})")
        emit('state', self.__get_state_dict())

    def __socket_get_header(self) -> None:
        self.dbgPrint(f"Answering get_header (Client {session['ClientID']})")
        emit('header', {'header': self.settings.getFrontendHeader()})

    def __socket_get_news(self) -> None:
        self.dbgPrint(f"Answering get_news (Client {session['ClientID']})")
        emit('news', {'news': self.settings.getFrontendNews()})

    def broadcastHeader(self, header: str) -> None:
        self.__broadcast('header', {'header': header})

    def broadcastNews(self, news: str) -> None:
        self.__broadcast('news', {'news': news})

    def broadcastAlarmEvent(self, alarmEvent: AlarmEvent) -> None:
        self.__broadcast('alarm_event', alarmEvent.toJSON())

    def broadcastDatabaseChanged(self) -> None:
        self.__broadcast('database_changed', { })

    def broadcastCalendarChanged(self) -> None:
        self.__broadcast('calendar_changed', { })

    def __get_stats_dict(self) -> Dict[str, Any]:
        statsDict = {
            'total': self.database.getEventStats(DatabaseTimespan.TOTAL, textOnly = True),
            'year': self.database.getEventStats(DatabaseTimespan.YEAR, textOnly = True),
            'month': self.database.getEventStats(DatabaseTimespan.MONTH, textOnly = True),
            'today': self.database.getEventStats(DatabaseTimespan.TODAY, textOnly = True)
        }

        return statsDict

    def __get_state_dict(self) -> Dict[str, Any]:
        if self.pluginManager is None:
            self.fatal("PluginManager not available")

        state: SourceState = self.pluginManager.getSourceState()

        stateDict = {
            'version': self.appInfo.version,
            'start_timestamp': self.appInfo.start,
            'source_state': int(state)
        }

        return stateDict
