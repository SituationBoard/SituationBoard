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
from backend.event.SettingEvent import SettingEvent
from backend.action.ActionUpdateSettings import ActionUpdateSettings

class Test_ActionUpdateSettings:

    INITIAL_HEADER = "initial header"
    UPDATED_HEADER = "updated header"

    INITIAL_NEWS = "initial news"
    UPDATED_NEWS = "updated news"

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_handle_event(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        settings = Settings(settingsFilename, appInfo.path)

        action = ActionUpdateSettings("", settings)

        # init and check initial settings
        settings.setFrontendHeader(Test_ActionUpdateSettings.INITIAL_HEADER)
        settings.setFrontendNews(Test_ActionUpdateSettings.INITIAL_NEWS)
        assert(settings.getFrontendHeader() == Test_ActionUpdateSettings.INITIAL_HEADER)
        assert(settings.getFrontendNews() == Test_ActionUpdateSettings.INITIAL_NEWS)

        # check that updating header setting succeeds
        settingEvent = SettingEvent()
        settingEvent.key = "header"
        settingEvent.value = Test_ActionUpdateSettings.UPDATED_HEADER
        settingEvent.flags = SettingEvent.FLAGS_VALID
        action.handleEvent(settingEvent)
        assert(settings.getFrontendHeader() == Test_ActionUpdateSettings.UPDATED_HEADER)

        # check that updating news setting succeeds
        settingEvent = SettingEvent()
        settingEvent.key = "news"
        settingEvent.value = Test_ActionUpdateSettings.UPDATED_NEWS
        settingEvent.flags = SettingEvent.FLAGS_VALID
        action.handleEvent(settingEvent)
        assert(settings.getFrontendNews() == Test_ActionUpdateSettings.UPDATED_NEWS)
