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

from backend.util.Plugin import Plugin
from backend.util.Settings import Settings

from backend.event.SourceEvent import SourceEvent

class Action(Plugin):
    """Action plugins implement the handling of SourceEvents and perform operations like updating the frontend.
    Action plugins have a unique name, implement the methods specified below
    and have to be registered with the PluginManager.
    They can retrieve settings from their respective section of the configuration file with the helper methods
    provided by the Plugin base class. In addition, they can print log/debug/error messages with the helper methods
    provided by the Module base class."""

    PLUGIN_TYPE = "action"

    def __init__(self, actionPluginName: str, instanceName: str, settings: Settings, multipleInstances: bool = False) -> None:
        """Constructs a Action plugin with a unique action name and access to settings and initializes it.

        :param actionPluginName: string representing a unique action plugin name
        :param instanceName: optional string representing a unique instance name of the action plugin
        :param settings: reference to the Settings object
        :param multipleInstances: boolean that specifies whether multiple (named) instances of this action plugin are supported"""
        super().__init__(Action.PLUGIN_TYPE, actionPluginName, instanceName, settings, multipleInstances)

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        """This method is called when a SourceEvent was received and implements
        the handling of SourceEvents by triggering plugin-specific actions.
        Depending on the actual plugin it may perform operations like updating databases,
        updating the frontend visualization or switching outlets on/off.
        In addition, the method may also update the SourceEvent (e.g. augment it with additional information).

        Important: The execution of this function should only consume a limited amount of time
        to avoid delaying other Action handlers or the processing of other SourceEvents.
        When network requests are made, ensure that a timeout prevents prolonged hanging of the thread.
        Handle errors/exceptions directly in your implementation and avoid crashing the whole backend
        (e.g. with unhandled exceptions).

        :param sourceEvent: SourceEvent (e.g. and AlarmEvent) that has to be handled by the plugin"""

    def handleCyclic(self) -> None:
        """This method is called periodically and enables plugin-specific housekeeping operations.
        It is often used to perform periodic operations or to undo an action performed by handleEvent
        after a certain time (e.g. switching outlets back off/on).

        Important: The execution of this function should only consume a limited amount of time
        to avoid delaying the processing of new SourceEvents and their Action handlers.
        When network requests are made, ensure that a timeout prevents prolonged hanging of the thread.
        Handle errors/exceptions directly in your implementation and avoid crashing the whole backend
        (e.g. with unhandled exceptions)."""
