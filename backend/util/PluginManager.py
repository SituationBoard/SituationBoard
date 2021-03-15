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

import importlib

from typing import List, Optional, TYPE_CHECKING

from backend.source.SourceDriver import SourceDriver, SourceState
from backend.source.MessageParser import MessageParser
from backend.event.SourceEvent import SourceEvent
from backend.action.Action import Action

from backend.util.Module import Module
from backend.util.Plugin import Plugin
from backend.util.Settings import Settings
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.data.Database import Database

if TYPE_CHECKING:
    from backend.api.WebSocket import WebSocket # pylint: disable=cyclic-import

class PluginManager(Module):
    """The PluginManager reads all configured SourceDriver, MessageParser and Action plugins from the configuration file
    and initializes them accordingly.
    During normal operation, it enables retrieving SourceEvents from all the configured SourceDriver plugins
    and handling of these SourceEvents by passing them to all configured Action plugins."""

    def __init__(self, settings: Settings, database: Database, webSocket: 'WebSocket', displayPowerManager: DisplayPowerManager) -> None:
        super().__init__("situationboard", settings)
        self.__settings = settings
        self.__database = database
        self.__webSocket = webSocket
        self.__displayPowerManager = displayPowerManager
        self.__sourcePlugins: List[SourceDriver] = []
        self.__actionPlugins: List[Action] = []

    def __loadParserPlugin(self, source: str, parserIdentifier: str) -> MessageParser:
        (parser, instanceName) = Plugin.splitPluginIdentifier(parserIdentifier)
        self.print(f"Init parser plugin {parser} (for source plugin {source})")
        parserPlugin: Optional[MessageParser] = None

        try:
            if source == "sms":
                if parser == "sms":
                    parserModule = importlib.import_module("backend.source.MessageParserSMS")
                    parserPlugin = parserModule.MessageParserSMS(instanceName, self.__settings) # type: ignore
                else:
                    self.fatal(f"Invalid parser plugin {parser} for source plugin {source}")
            elif source == "mail":
                if parser == "mail":
                    parserModule = importlib.import_module("backend.source.MessageParserMail")
                    parserPlugin = parserModule.MessageParserMail(instanceName, self.__settings) # type: ignore
                else:
                    self.fatal(f"Invalid parser plugin {parser} for source plugin {source}")
            else:
                self.fatal(f"No parser plugin available/required for source plugin {source}")

        except Exception as e:
            self.fatal(f"An exception occurred during init of parser plugin {parser}", e)

        if parserPlugin is None:
            self.fatal(f"No parser plugin for source plugin {source}")

        return parserPlugin

    def initPlugins(self) -> None:
        self.__initSourcePlugins()
        self.__initActionPlugins()

    def __initSourcePlugins(self) -> None:
        if len(self.__sourcePlugins) > 0:
            return

        sources = self.__settings.getBackendSources()
        for sourceIdentifier in sources:
            (source, instanceName) = Plugin.splitPluginIdentifier(sourceIdentifier)
            self.print(f"Init source plugin {source}")
            sourcePlugin: Optional[SourceDriver] = None

            try:
                if source == "sms":
                    parserIdentifier = self.__settings.getString("source_sms", "parser", "sms")
                    parserPlugin = self.__loadParserPlugin(source, parserIdentifier)
                    sourceModule = importlib.import_module("backend.source.SourceDriverSMS")
                    sourcePlugin = sourceModule.SourceDriverSMS(instanceName, self.__settings, parserPlugin) # type: ignore
                elif source == "binary":
                    sourceModule = importlib.import_module("backend.source.SourceDriverBinary")
                    sourcePlugin = sourceModule.SourceDriverBinary(instanceName, self.__settings) # type: ignore # no parser required
                elif source == "dummy":
                    sourceModule = importlib.import_module("backend.source.SourceDriverDummy")
                    sourcePlugin = sourceModule.SourceDriverDummy(instanceName, self.__settings) # type: ignore # no parser required
                elif source == "scanner":
                    self.fatal("Scanner source plugin not yet implemented")
                elif source == "webapi":
                    self.fatal("Web API source plugin not yet implemented")
                elif source == "fax":
                    self.fatal("Fax source plugin not yet implemented")
                elif source == "mail":
                    parserIdentifier = self.__settings.getString("source_mail", "parser", "mail")
                    parserPlugin = self.__loadParserPlugin(source, parserIdentifier)
                    sourceModule = importlib.import_module("backend.source.SourceDriverMail")
                    sourcePlugin = sourceModule.SourceDriverMail(instanceName, self.__settings, parserPlugin) # type: ignore
                else:
                    self.fatal(f"Invalid source plugin {source}")

            except Exception as e:
                self.fatal(f"An exception occurred during init of source plugin {source}", e)

            if sourcePlugin is not None:
                self.__sourcePlugins.append(sourcePlugin)

        if len(self.__sourcePlugins) == 0:
            self.fatal("No source plugins configured!")

    def __initActionPlugins(self) -> None:
        if len(self.__actionPlugins) > 0:
            return

        actions = self.__settings.getBackendActions()
        for actionIdentifier in actions:
            (action, instanceName) = Plugin.splitPluginIdentifier(actionIdentifier)

            self.print(f"Init action plugin {action}")
            actionPlugin: Optional[Action] = None

            try:
                if action == "search_location":
                    actionModule = importlib.import_module("backend.action.ActionSearchLocation")
                    actionPlugin = actionModule.ActionSearchLocation(instanceName, self.__settings) # type: ignore
                elif action == "update_database":
                    actionModule = importlib.import_module("backend.action.ActionUpdateDatabase")
                    actionPlugin = actionModule.ActionUpdateDatabase(instanceName, self.__settings, self.__database, self.__webSocket) # type: ignore
                elif action == "update_settings":
                    actionModule = importlib.import_module("backend.action.ActionUpdateSettings")
                    actionPlugin = actionModule.ActionUpdateSettings(instanceName, self.__settings) # type: ignore
                elif action == "update_frontend":
                    actionModule = importlib.import_module("backend.action.ActionUpdateFrontend")
                    actionPlugin = actionModule.ActionUpdateFrontend(instanceName, self.__settings, self.__webSocket) # type: ignore
                elif action == "update_calendar":
                    actionModule = importlib.import_module("backend.action.ActionUpdateCalendar")
                    actionPlugin = actionModule.ActionUpdateCalendar(instanceName, self.__settings, self.__webSocket) # type: ignore
                elif action == "activate_screen":
                    actionModule = importlib.import_module("backend.action.ActionActivateScreen")
                    actionPlugin = actionModule.ActionActivateScreen(instanceName, self.__settings, self.__displayPowerManager) # type: ignore
                elif action == "send_poweralarm":
                    actionModule = importlib.import_module("backend.action.ActionSendMessagePowerAlarm")
                    actionPlugin = actionModule.ActionSendMessagePowerAlarm(instanceName, self.__settings) # type: ignore
                elif action == "toggle_outlet":
                    actionModule = importlib.import_module("backend.action.ActionToggleOutlet")
                    actionPlugin = actionModule.ActionToggleOutlet(instanceName, self.__settings) # type: ignore
                elif action == "toggle_output":
                    actionModule = importlib.import_module("backend.action.ActionToggleOutput")
                    actionPlugin = actionModule.ActionToggleOutput(instanceName, self.__settings) # type: ignore
                elif action == "write_file":
                    actionModule = importlib.import_module("backend.action.ActionWriteFile")
                    actionPlugin = actionModule.ActionWriteFile(instanceName, self.__settings) # type: ignore
                else:
                    self.fatal(f"Invalid action plugin {action}")

            except Exception as e:
                self.fatal(f"An exception occurred during init of action plugin {action}", e)

            if actionPlugin is not None:
                self.__actionPlugins.append(actionPlugin)

        if len(self.__actionPlugins) == 0:
            self.fatal("No action plugins configured!")

    def retrieveEvent(self) -> Optional[SourceEvent]:
        """Tries to retrieve the next SourceEvent by asking the configured SourceDrivers for SourceEvents
        in the same order as specified in the configuration file.
        The first SourceEvent found is returned immediately, postponing the handling of SourceEvents
        available from other SourceDrivers.

        :return: SourceEvent (or a subclass thereof) if a event was available, None otherwise"""
        sourceEvent = None
        for sourceDriver in self.__sourcePlugins:
            sourceEvent = None
            try:
                sourceEvent = sourceDriver.retrieveEvent()
            except Exception as e:
                #sourceEvent = None
                #self.error("{sourceDriver}.retrieveEvent() caused an unhandled exception", e)
                self.fatal(f"{sourceDriver}.retrieveEvent() caused an unhandled exception", e)

            if sourceEvent is not None:
                break

        return sourceEvent

    def getSourceState(self) -> SourceState:
        """Returns the overall state of all configured SourceDriver plugins
        (for visualization in the status bar of the frontend).

        :return: SourceState representing the overall state of all sources"""
        state = SourceState.OK
        for sourceDriver in self.__sourcePlugins:
            s = SourceState.ERROR
            try:
                s = sourceDriver.getSourceState()
            except Exception as e:
                s = SourceState.ERROR
                self.error(f"{sourceDriver}.getSourceState() caused an unhandled exception", e)

            if s != SourceState.OK:
                state = SourceState.ERROR
                # break

        return state

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        """Handles a SourceEvent by passing the event to all the Action plugins
        in the same order as specified in the configuration file.

        :param sourceEvent: SourceEvent that has to be handled by all the Action plugins"""
        for actionHandler in self.__actionPlugins:
            try:
                actionHandler.handleEvent(sourceEvent)
            except Exception as e:
                self.error(f"{actionHandler}.handleEvent(sourceEvent) caused an unhandled exception", e)


    def handleCyclic(self) -> None:
        """Allows Action plugins to perform housekeeping operations
        in the same order as specified in the configuration file."""
        for actionHandler in self.__actionPlugins:
            try:
                actionHandler.handleCyclic()
            except Exception as e:
                self.error(f"{actionHandler}.handleCyclic() raised an unhandled exception", e)
