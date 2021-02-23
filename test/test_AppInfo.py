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
import re

from backend.util.AppInfo import AppInfo

class Test_AppInfo:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        self.appInfo = AppInfo()

    def test_app_info_name(self) -> None:
        # check that we have a valid application name
        assert(self.appInfo.name == "SituationBoard")

    def test_app_info_path(self) -> None:
        # check that we retrieved a valid application path
        assert(self.appInfo.path != "")
        assert(os.path.exists(self.appInfo.path))
        assert(os.path.exists(os.path.join(self.appInfo.path, "SituationBoard.py")))

    def test_app_info_version(self) -> None:
        # check that we retrieved a valid application version from the version file
        assert(self.appInfo.version != "")
        assert(self.appInfo.version != "0.0")
        assert("\n" not in self.appInfo.version)
        assert(re.match(r"^(\d+\.)?(\d+\.)?(\*|\d+)$", self.appInfo.version))

    def test_app_info_pid(self) -> None:
        # check that we retrieved the correct process ID
        assert(self.appInfo.pid == os.getpid())
