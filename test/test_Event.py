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

import datetime

from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent

class Test_Database:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_source_event(self) -> None:
        se = SourceEvent()
        assert(se.updated is False)

        se.markAsHandled()
        assert(se.updated is True)

        ts = datetime.datetime.now() - datetime.timedelta(seconds=5)
        se.timestamp = datetime.datetime.strftime(ts, SourceEvent.TIMESTAMP_FORMAT)
        assert(se.isOutdated(0) is False)
        assert(se.isOutdated(10) is False)
        assert(se.isOutdated(1) is True)

    def test_alarm_event(self) -> None:
        ae = AlarmEvent()
        assert(ae.updated is False)

        ae.markAsHandled()
        assert(ae.updated is True)

        ts = datetime.datetime.now() - datetime.timedelta(seconds=5)
        ae.timestamp = datetime.datetime.strftime(ts, SourceEvent.TIMESTAMP_FORMAT)
        assert(ae.isOutdated(0) is False)
        assert(ae.isOutdated(10) is False)
        assert(ae.isOutdated(1) is True)

        ats = datetime.datetime.now() - datetime.timedelta(seconds=30)
        ae.alarmTimestamp = datetime.datetime.strftime(ats, AlarmEvent.TIMESTAMP_FORMAT)
        assert(ae.isOutdated(0) is False)
        assert(ae.isOutdated(60) is False)
        assert(ae.isOutdated(15) is True)

        ae.flags = AlarmEvent.FLAGS_VALID
        assert(ae.valid is True)
        assert(ae.invalid is False)
        assert(ae.binary is False)

        ae.flags = AlarmEvent.FLAGS_INVALID
        assert(ae.valid is False)
        assert(ae.invalid is True)
        assert(ae.binary is False)

        ae.flags = AlarmEvent.FLAGS_BINARY
        assert(ae.valid is False)
        assert(ae.invalid is False)
        assert(ae.binary is True)
