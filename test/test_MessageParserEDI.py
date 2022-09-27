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
import datetime
import shutil

from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.source.MessageParserEDI import MessageParserEDI

#from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
#from backend.event.SettingEvent import SettingEvent
#from backend.event.UnhandledEvent import UnhandledEvent

#TODO: add tests for EDI parser

class Test_MessageParserEDI:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        appInfo = AppInfo()
        settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
        settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")

        shutil.copy(settingsFilenameOrig, settingsFilename)

        s = Settings(settingsFilename, appInfo.path)

        self.p = MessageParserEDI("", s)

        self.defaultSender = "127.0.0.1"
        self.defaultTimestamp = datetime.datetime.now().strftime(AlarmEvent.TIMESTAMP_FORMAT)
        self.eid = 1302

    def test_todo(self) -> None:
        assert(True)
