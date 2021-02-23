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

from enum import IntEnum

from typing import Optional, List

from backend.util.Plugin import Plugin
from backend.util.Settings import Settings
from backend.source.MessageParser import MessageParser
from backend.event.SourceEvent import SourceEvent

class SourceState(IntEnum):
    OK    = 0
    ERROR = 1

class SourceDriver(Plugin):
    """SourceDriver plugins implement the reception of SourceEvents like an alarm SMS from sources like a cellular modem.
    SourceDriver plugins have a unique name, implement the methods specified below
    and have to be registered with the PluginManager.
    They can retrieve settings from their respective section of the configuration file with the helper methods
    provided by the Plugin base class. In addition, they can print log/debug/error messages with the helper methods
    provided by the Module base class."""

    PLUGIN_TYPE = "source"

    def __init__(self, sourcePluginName: str, instanceName: str, settings: Settings, parser: Optional[MessageParser] = None, multipleInstances: bool = False) -> None:
        """Constructs a SourceDriver plugin with a unique source name and access to settings and initializes it.

        :param sourcePluginName: string representing a unique source plugin name
        :param instanceName: optional string representing a unique instance name of the source plugin
        :param settings: reference to the Settings object
        :param parser: reference to an optional parser plugin (that is used by the source plugin)
        :param multipleInstances: boolean that specifies whether multiple (named) instances of this source plugin are supported"""
        super().__init__(SourceDriver.PLUGIN_TYPE, sourcePluginName, instanceName, settings, multipleInstances)
        self.parser = parser

    def retrieveEvent(self) -> Optional[SourceEvent]:
        """This method is called periodically by the background task in order to
        retrieve SourceEvents from the SourceDriver plugin.

        Important: The execution of this function should only consume a limited amount of time
        to avoid delaying Action handlers or the processing of other SourceEvents.
        When network requests are made, ensure that a timeout prevents prolonged hanging of the thread.
        Handle errors/exceptions directly in your implementation and avoid crashing the whole backend
        (e.g. with unhandled exceptions).

        :return: SourceEvent, a subclass of SourceEvent (e.g. AlarmEvent) or None"""
        return None

    def getSourceState(self) -> SourceState:
        """This method is called periodically to retrieve the current state of the source.
        It represents whether the source is working as intended or not (e.g. no cell reception)
        and is visualized in the status bar of the frontend.

        :return: SourceState (e.g. SourceState.OK or SourceState.ERROR)"""
        return SourceState.ERROR

    @staticmethod
    def isSenderAllowed(allowlist: List[str], denylist: List[str], sender: str) -> bool:
        """This helper function allows the validation of a sender against allowlists and denylists.

        :param allowlist: List of strings with all allowed senders (e.g. phone numbers)
        :param denylist:  List of stings with all denied senders (e.g. phone numbers)
        :param sender: Strings representing the sender (e.g. phone number)

        :return: bool (True = sender is allowed; False = sender is denied)"""
        if len(allowlist) != 0 and sender not in allowlist:
            return False

        if len(denylist) != 0 and sender in denylist:
            return False

        return True
