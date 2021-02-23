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

from backend.source.SourceDriver import SourceDriver

class Test_SenderFilter:

    def setup_class(self) -> None:
        #pylint: disable=W0201
        pass

    def test_allowed_no_lists(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=[],
                                            denylist=[],
                                            sender="+49123") is True)

    def test_blocked_in_both(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49123"],
                                            denylist=["+49123"],
                                            sender="+49123") is False)

    def test_blocked_in_black(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=[],
                                            denylist=["+49123"],
                                            sender="+49123") is False)

    def test_allowed_in_white(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49123"],
                                            denylist=[],
                                            sender="+49123") is True)

    def test_blocked_not_in_both(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49000"],
                                            denylist=["+49000"],
                                            sender="+49123") is False)

    def test_allowed_not_in_black(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=[],
                                            denylist=["+49000"],
                                            sender="+49123") is True)

    def test_blocked_not_in_white(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49000"],
                                            denylist=[],
                                            sender="+49123") is False)

    def test_blocked_mult1_in_both(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49000", "+49123"],
                                            denylist=["+49123"],
                                            sender="+49123") is False)

    def test_blocked_mult1_in_black(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=[],
                                            denylist=["+49000", "+49123"],
                                            sender="+49123") is False)

    def test_allowed_mult1_in_white(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49000", "+49123"],
                                            denylist=[],
                                            sender="+49123") is True)

    def test_blocked_mult2_in_both(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49123", "+49000"],
                                            denylist=["+49123"],
                                            sender="+49123") is False)

    def test_blocked_mult2_in_black(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=[],
                                            denylist=["+49123", "+49000"],
                                            sender="+49123") is False)

    def test_allowed_mult2_in_white(self) -> None:
        assert(SourceDriver.isSenderAllowed(allowlist=["+49123", "+49000"],
                                            denylist=[],
                                            sender="+49123") is True)
