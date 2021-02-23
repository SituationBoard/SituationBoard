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
import time

class AppInfo:
    """The AppInfo class makes application information available to other modules.
    This information includes the application version, process ID and path."""

    APP_VERSION_FILENAME = "VERSION"

    def __init__(self) -> None:
        self.__appName = "SituationBoard"
        self.__appVersion = "0.0"

        self.__appStartTimestamp = time.time_ns()
        self.__appProcessID = os.getpid()

        pUtil = os.path.dirname(os.path.abspath(__file__))
        pBackend = os.path.join(pUtil, os.pardir)
        pApp = os.path.join(pBackend, os.pardir)
        self.__appPath = os.path.abspath(pApp)

        try:
            versionFilePath = os.path.join(self.__appPath, AppInfo.APP_VERSION_FILENAME)
            with open(versionFilePath, "r") as versionFile:
                self.__appVersion = versionFile.read().strip()
        except Exception:
            pass

    @property
    def name(self) -> str:
        return self.__appName

    @property
    def version(self) -> str:
        return self.__appVersion

    @property
    def path(self) -> str:
        return self.__appPath

    @property
    def pid(self) -> int:
        return self.__appProcessID

    @property
    def start(self) -> int:
        return self.__appStartTimestamp

    def __str__(self) -> str:
        return f"{self.name} {self.version}"

    def __repr__(self) -> str:
        return f"{self.name} {self.version}"
