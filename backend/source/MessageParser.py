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

from backend.util.Plugin import Plugin
from backend.util.Settings import Settings
from backend.event.SourceEvent import SourceEvent

class MessageParser(Plugin):
    """MessageParser plugins help SourceDriver plugins to parse received SourceEvents
    that consist of text messages (e.g. SMS).
    MessageParser plugins have a unique name, implement the methods specified below
    and have to be registered with the PluginManager.
    They can retrieve settings from their respective section of the configuration file with the helper methods
    provided by the Plugin base class. In addition, they can print log/debug/error messages with the helper methods
    provided by the Module base class."""

    PLUGIN_TYPE = "parser"

    def __init__(self, parserPluginName: str, instanceName: str, settings: Settings, multipleInstances: bool = False) -> None:
        """Constructs a MessageParser plugin with a unique parser name and access to settings and initializes it.

        :param parserPluginName: string representing a unique parser plugin name
        :param instanceName: optional string representing a unique instance name of the parser plugin
        :param settings: reference to the Settings object
        :param multipleInstances: boolean that specifies whether multiple (named) instances of this parser plugin are supported"""
        super().__init__(MessageParser.PLUGIN_TYPE, parserPluginName, instanceName, settings, multipleInstances)

    def parseMessage(self, sourceEvent: SourceEvent, lastEvent: Optional[SourceEvent]) -> Optional[SourceEvent]:
        """This method is called by a SourceDriver plugin to parse the raw content (i.e. plain text) of a SourceEvent.
        It returns a SourceEvent (e.g. an AlarmEvent) that is augmented with all the parsed information.
        The last SourceEvent from the corresponding source is provided to this method to allow
        merging of consecutive source events.

        :param sourceEvent: SourceEvent (with raw data) that has to be parsed
        :param lastEvent: Last received (and parsed) SourceEvent or a subclass thereof (for potential merges)

        :return: Parsed SourceEvent (typically a subclass of SourceEvent like AlarmEvent) augmented with the parsed information"""
        return None
