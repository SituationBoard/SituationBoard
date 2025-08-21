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

import signal

from types import TracebackType
from typing import Iterable
from threading import Lock

class SignalLock:
    def __init__(self, signals: Iterable[int]):
        self.signals = signals
        self.lock = Lock()
        self.oldSignalMask: set[int | signal.Signals] = set()

    def acquire(self) -> None:
        self.oldSignalMask = signal.pthread_sigmask(signal.SIG_BLOCK, self.signals)
        self.lock.acquire() #pylint: disable=consider-using-with

    def release(self) -> None:
        self.lock.release()
        signal.pthread_sigmask(signal.SIG_SETMASK, self.oldSignalMask)

    def __enter__(self) -> 'SignalLock':
        self.acquire()
        return self

    def __exit__(self, exception_type: type[BaseException] | None, exception_value: BaseException | None, exception_traceback: TracebackType | None) -> None:
        self.release()
