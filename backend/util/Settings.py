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
import configparser

from typing import List

from backend.util.Module import Module
from backend.util.StringConverter import StringConverter

class Settings(Module):
    """The Settings class is responsible for reading/writing of user settings from/to the configuration file.
    It is mainly responsible for backend and frontend settings, but also provides the infrastructure which allows
    modules and plugins to have additional settings in their own sections of the configuration file."""

    # Sections
    SECTION_BACKEND                = "backend"
    SECTION_FRONTEND               = "frontend"

    # Keys of writable settings
    KEY_FRONTEND_HEADER            = "header"
    KEY_FRONTEND_NEWS              = "news"

    # Defaults of writable settings
    DEFAULT_FRONTEND_HEADER        = "Feuerwehr Musterdorf"  # organisation shown as header in standby mode
    DEFAULT_FRONTEND_NEWS          = "Herzlich Willkommen"   # news shown as message below header

    def __init__(self, configPath: str, appPath: str, forceDebug: bool = False) -> None:
        super().__init__("settings", settings = None, debug = False)
        self.__filename = configPath
        self.__appPath = appPath
        self.__forceDebug = forceDebug
        self.__config = configparser.RawConfigParser()

        self.print("Reading settings from config file")
        try:
            with open(self.__filename, 'r') as configFile:
                self.__config.read_file(configFile, self.__filename)
        except Exception:
            self.fatal(f"Could not read config file ({self.__filename})")

    def store(self) -> None:
        self.print("Writing settings to config file")
        try:
            with open(self.__filename, 'w') as configFile:
                self.__config.write(configFile)
        except Exception:
            self.error(f"Could not write config file ({self.__filename}")

    def getString(self, section: str, key: str, default: str) -> str:
        try:
            singleLineValue = self.__config.get(section, key)
            value = StringConverter.singleline2string(singleLineValue)
        except Exception:
            value = default

        self.dbgPrint(f"{section}/{key} = {value} (default = {default})")
        return value

    def getBoolean(self, section: str, key: str, default: bool) -> bool:
        try:
            value = self.__config.getboolean(section, key)
        except Exception:
            value = default

        self.dbgPrint(f"{section}/{key} = {value} (default = {default})")
        return value

    def getFloat(self, section: str, key: str, default: float) -> float:
        try:
            value = self.__config.getfloat(section, key)
        except Exception:
            value = default

        self.dbgPrint(f"{section}/{key} = {value} (default = {default})")
        return value

    def getInt(self, section: str, key: str, default: int) -> int:
        try:
            value = self.__config.getint(section, key)
        except Exception:
            value = default

        self.dbgPrint(f"{section}/{key} = {value} (default = {default})")
        return value

    def getList(self, section: str, key: str, default: List[str]) -> List[str]:
        try:
            text = self.__config.get(section, key)
            value = [x.strip() for x in text.split(',') if x.strip() != ""]
        except Exception:
            value = default

        if self.isDebug():
            strValue = ','.join(map(str, value))
            strDefault = ','.join(map(str, default))
            self.dbgPrint(f"{section}/{key} = [{strValue}] (default = [{strDefault}])")

        return value

    def getFilename(self, section: str, key: str, default: str) -> str:
        try:
            filename = self.__config.get(section, key)
        except Exception:
            filename = default

        # filename = filename.replace("$SBPATH", self.__appPath)
        if not os.path.isabs(filename):
            filename = os.path.join(self.__appPath, filename)

        self.dbgPrint(f"{section}/{key} = {filename} (default = {default})")
        return filename

    def getOption(self, section: str, key: str, options: List[str], default: str) -> str:
        try:
            option = self.__config.get(section, key)
            if option not in options:
                option = default
        except Exception:
            option = default

        self.dbgPrint(f"{section}/{key} = {option} (default = {default})")
        return option

    def __setSetting(self, section: str, key: str, value: str) -> bool:
        try:
            if not self.__config.has_section(section):
                self.__config.add_section(section)

            self.__config.set(section, key, value)
            self.print(f"Updated setting {section}/{key} with value {value}")
            return True
        except Exception:
            self.error(f"Failed to update setting {section}/{key} with value {value}")
            return False

    def setString(self, section: str, key: str, value: str) -> bool:
        singleLineValue = StringConverter.string2singleline(value)
        return self.__setSetting(section, key, singleLineValue)

    def setBoolean(self, section: str, key: str, value: bool) -> bool:
        return self.__setSetting(section, key, str(value))

    def setFloat(self, section: str, key: str, value: float) -> bool:
        return self.__setSetting(section, key, str(value))

    def setInt(self, section: str, key: str, value: int) -> bool:
        return self.__setSetting(section, key, str(value))

    def getForceDebug(self) -> bool:
        return self.__forceDebug

    # Backend Settings

    def getBackendServerHost(self) -> str:
        return self.getString(Settings.SECTION_BACKEND, "server_host", "127.0.0.1")

    def getBackendServerPort(self) -> int:
        return self.getInt(Settings.SECTION_BACKEND, "server_port", 5000)

    def getBackendDebug(self) -> bool:
        if self.getForceDebug():
            return True

        return self.getBoolean(Settings.SECTION_BACKEND, "debug", False)

    def getBackendReloader(self) -> bool:
        return self.getBoolean(Settings.SECTION_BACKEND, "reloader", False)

    def getBackendWebAPI(self) -> bool:
        return self.getBoolean(Settings.SECTION_BACKEND, "web_api", False)

    def getBackendLoopSleepDuration(self) -> int:
        return self.getInt(Settings.SECTION_BACKEND, "loop_sleep_duration", 1) # in seconds

    def getBackendSources(self) -> List[str]:
        return self.getList(Settings.SECTION_BACKEND, "sources", [])

    def getBackendActions(self) -> List[str]:
        return self.getList(Settings.SECTION_BACKEND, "actions", [])

    # Frontend Settings

    def getFrontendHeader(self) -> str:
        return self.getString(Settings.SECTION_FRONTEND, Settings.KEY_FRONTEND_HEADER, Settings.DEFAULT_FRONTEND_HEADER)

    def setFrontendHeader(self, value: str) -> bool:
        return self.setString(Settings.SECTION_FRONTEND, Settings.KEY_FRONTEND_HEADER, value)

    def getFrontendNews(self) -> str:
        return self.getString(Settings.SECTION_FRONTEND, Settings.KEY_FRONTEND_NEWS, Settings.DEFAULT_FRONTEND_NEWS)

    def setFrontendNews(self, value: str) -> bool:
        return self.setString(Settings.SECTION_FRONTEND, Settings.KEY_FRONTEND_NEWS, value)

    def getFrontendDebug(self) -> bool:
        return self.getBoolean(Settings.SECTION_FRONTEND, "debug", False)

    def getFrontendLanguage(self) -> str:
        availableLanguages = ["en", "en_us", "en_gb", "de"]
        defaultLanguage = "en"
        return self.getOption(Settings.SECTION_FRONTEND, "language", availableLanguages, defaultLanguage)

    def getFrontendAlarmDuration(self) -> int:
        return self.getInt(Settings.SECTION_FRONTEND, "alarm_duration", 60 * 60) # in seconds - default 1 hour

    def getFrontendAlarmShowMaps(self) -> str:
        availableMaps = ["none", "location", "route", "both"]
        defaultMaps = "both"
        return self.getOption(Settings.SECTION_FRONTEND, "alarm_show_maps", availableMaps, defaultMaps)

    def getFrontendCalendarURL(self) -> str:
        return self.getString(Settings.SECTION_FRONTEND, "calendar_url", "data/calendar.ics")

    def getFrontendCalendarUpdateDuration(self) -> int:
        return self.getInt(Settings.SECTION_FRONTEND, "calendar_update_duration", 0) # in seconds - default 0 = never

    def getFrontendStandbyShowStatistics(self) -> bool:
        return self.getBoolean(Settings.SECTION_FRONTEND, "standby_show_statistics", True)

    def getFrontendStandbyShowClock(self) -> bool:
        return self.getBoolean(Settings.SECTION_FRONTEND, "standby_show_clock", True)

    def getFrontendPageReloadDuration(self) -> int:
        return self.getInt(Settings.SECTION_FRONTEND, "page_reload_duration", 0) # in seconds - default 0 = never

    def getFrontendMapService(self) -> str:
        avaiableServices = ["osm", "osm_openlayers", "osm_leaflet", "google"]
        defaultService = "osm"
        return self.getOption(Settings.SECTION_FRONTEND, "map_service", avaiableServices, defaultService)

    def getFrontendMapAPIKey(self) -> str:
        return self.getString(Settings.SECTION_FRONTEND, "map_api_key", "")

    def getFrontendMapZoom(self) -> float:
        return self.getFloat(Settings.SECTION_FRONTEND, "map_zoom", 19.0)

    def getFrontendMapType(self) -> str:
        availableTypes = ["default", "roadmap", "satellite", "hybrid", "terrain"]
        defaultType = "default"
        return self.getOption(Settings.SECTION_FRONTEND, "map_type", availableTypes, defaultType)

    def getFrontendMapEmergencyLayer(self) -> str:
        availableLayers = ["none", "medical", "fire", "all"]
        defaultLayer = "all"
        return self.getOption(Settings.SECTION_FRONTEND, "map_emergency_layer", availableLayers, defaultLayer)

    def getFrontendMapHomeLatitude(self) -> float:
        return self.getFloat(Settings.SECTION_FRONTEND, "map_home_latitude", 0.0)

    def getFrontendMapHomeLongitude(self) -> float:
        return self.getFloat(Settings.SECTION_FRONTEND, "map_home_longitude", 0.0)

    def getFrontendShowSplashScreen(self) -> bool:
        return self.getBoolean(Settings.SECTION_FRONTEND, "show_splash_screen", True)
