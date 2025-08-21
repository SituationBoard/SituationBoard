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

from typing import Dict, List, Tuple, TYPE_CHECKING

from backend.util.Module import Module

if TYPE_CHECKING:
    from backend.util.Settings import Settings

class Plugin(Module):
    """The Plugin class implements functionality that is required by all kinds of plugins
    and offers methods to retrieve plugin-specific settings from the configuration file.
    Plugins have a unique identifier (consisting of a plugin type and a plugin name).
    This identifier is used to identify the corresponding section in the configuration file.
    In addition, the identifier is also prepended to all the log/debug/error messages of the plugin."""

    NAME_SEPARATOR = ":"

    existingInstances: Dict[str, List[str]] = {}

    def __init__(self, pluginType: str, pluginName: str, instanceName: str, settings: 'Settings', multipleInstances: bool = False) -> None: #pylint: disable=too-many-positional-arguments
        """Constructs a Plugin of a certain type with a specific name and access to settings and initializes it.

        :param pluginType: string representing the type as specified by subclasses of Plugin (like SourceDriver, MessageParser and Action)
        :param pluginName: string representing a unique plugin name within the specified type-class
        :param instanceName: optional string representing a unique instance name of the plugin
        :param settings: reference to the Settings object
        :param multipleInstances: boolean that specifies whether multiple (named) instances of this plugin are supported"""

        fullPluginName = pluginType + Plugin.NAME_SEPARATOR + pluginName
        if instanceName != "":
            super().__init__(fullPluginName + Plugin.NAME_SEPARATOR + instanceName, settings)
        else:
            super().__init__(fullPluginName, settings)

        self.pluginType = pluginType
        self.pluginName = pluginName
        self.instanceName = instanceName
        self.settings = settings

        if fullPluginName not in Plugin.existingInstances:
            Plugin.existingInstances[fullPluginName] = []

        instancesOfPlugin = Plugin.existingInstances[fullPluginName]

        if len(instancesOfPlugin) > 0:
            #TODO: move these (unique name, multi instance) checks into the PluginManager ?

            if multipleInstances is False:
                self.fatal("Only one instances of this plugin is supported")

            if instanceName in instancesOfPlugin:
                iName = instanceName if instanceName != "" else "<NONE>"
                self.fatal(f"Instance name ({iName}) is already in use for this plugin")

        instancesOfPlugin.append(instanceName)

    def isDebug(self) -> bool:
        """Returns whether the plugin is in debug mode (True) or not (False).

        :return: bool whether debug mode is active
        """
        if self.settings.getForceDebug():
            return True

        return self.getSettingBoolean("debug", False)

    def getSettingString(self, key: str, default: str) -> str:
        """Retrieves a string setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param default: default string that is used when the setting is not specified in the configuration file
        :return: string representing the value of the setting"""
        return self.settings.getString(self.moduleName, key, default)

    def getSettingBoolean(self, key: str, default: bool) -> bool:
        """Retrieves a bool setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param default: default bool that is used when the setting is not specified in the configuration file
        :return: bool representing the value of the setting"""
        return self.settings.getBoolean(self.moduleName, key, default)

    def getSettingInt(self, key: str, default: int) -> int:
        """Retrieves an int setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param default: default int that is used when the setting is not specified in the configuration file
        :return: int representing the value of the setting"""
        return self.settings.getInt(self.moduleName, key, default)

    def getSettingFloat(self, key: str, default: float) -> float:
        """Retrieves a float setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param default: default float that is used when the setting is not specified in the configuration file
        :return: float representing the value of the setting"""
        return self.settings.getFloat(self.moduleName, key, default)

    def getSettingList(self, key: str, default: List[str]) -> List[str]:
        """Retrieves a list (of strings) setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param default: default list of strings that is used when the setting is not specified in the configuration file
        :return: list of strings representing the value of the setting"""
        return self.settings.getList(self.moduleName, key, default)

    def getSettingFilename(self, key: str, default: str) -> str:
        """Retrieves a filename setting that is specified by a unique key from the configuration section of the plugin.
        Important: Relative filenames are automatically prepended with the root directory of the backend.

        :param key: string representing the unique key name of the plugin setting
        :param default: string representing the default filename that is used when the setting is not specified in the configuration file
        :return: string with the absolute filename representing the value of the setting"""
        return self.settings.getFilename(self.moduleName, key, default)

    def getSettingOption(self, key: str, options: List[str], default: str) -> str:
        """Retrieves an option setting that is specified by a unique key from the configuration section of the plugin.

        :param key: string representing the unique key name of the plugin setting
        :param options: list of strings representing all available options
        :param default: string representing the default option that is used when the setting is not specified in the configuration file
        :return: string with the option representing the value of the setting"""
        return self.settings.getOption(self.moduleName, key, options, default)

    @classmethod
    def splitPluginIdentifier(cls, pluginIdentifier: str) -> Tuple[str, str]:
        parts = pluginIdentifier.split(Plugin.NAME_SEPARATOR, 1)
        pluginName = parts[0]
        instanceName = "" if len(parts) < 2 else parts[1]
        return (pluginName, instanceName)
