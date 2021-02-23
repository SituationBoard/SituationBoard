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

from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings

class Test_Settings:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_settings(self) -> None:
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        s = Settings(settingsFilename, appInfo.path)

        frontendHeaderTest = "Frontend\n\"Complicated\"\tHeader\\=Test=1234"
        assert(s.getFrontendHeader() != frontendHeaderTest)
        s.setFrontendHeader(frontendHeaderTest)
        assert(s.getFrontendHeader() == frontendHeaderTest)

        frontendNewsTest = "Frontend\n\"Complicated\"\tNews\\=Test=1234"
        assert(s.getFrontendNews() != frontendNewsTest)
        s.setFrontendNews(frontendNewsTest)
        assert(s.getFrontendNews() == frontendNewsTest)

        test_string = "test_string"
        test_boolean = True
        test_int = 112
        test_float = 1.12

        s.setString("test", "test_string", test_string)
        s.setBoolean("test", "test_boolean", test_boolean)
        s.setInt("test", "test_int", test_int)
        s.setFloat("test", "test_float", test_float)

        s.store()

        sr = Settings(settingsFilename, appInfo.path)

        assert(sr.getFrontendHeader() == frontendHeaderTest)
        assert(sr.getFrontendNews() == frontendNewsTest)

        assert(sr.getString("test", "test_string", "") == test_string)
        assert(sr.getBoolean("test", "test_boolean", not test_boolean) == test_boolean)
        assert(sr.getInt("test", "test_int", 0) == test_int)
        assert(sr.getFloat("test", "test_float", 0.0) == test_float)

        defaultSources = ["dummy"]
        defaultActions = ["search_location", "update_database", "update_settings", "update_frontend" , "update_calendar"]
        defaultLanguage = "de"
        assert(sr.getBackendSources() == defaultSources)    # test getList and correct default sources
        assert(sr.getBackendActions() == defaultActions)    # test getList and correct default actions
        assert(sr.getFrontendLanguage() == defaultLanguage) # test getOption and correct default language
