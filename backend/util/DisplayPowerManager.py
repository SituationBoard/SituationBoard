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

import subprocess

from backend.util.Module import Module
from backend.util.Settings import Settings

class DisplayPowerManager(Module):
    """The DisplayPowerManager controls the power state of the attached display (e.g. TV screen) via CEC.
    It allows the ActivateScreen action to wake the display from standby mode in case of an alarm event."""

    def __init__(self, settings: Settings, tvDevice: int = 0) -> None:
        super().__init__("cec", settings = None, debug = False)
        self.tv = tvDevice # TV should always be 0
        # self.dbgPrint(self.executeCECCommand("scan"))

    def powerOn(self) -> bool:
        wasON = self.getState()
        result = self.executeCECCommand(f"on {self.tv}")
        self.dbgPrint(f"powerOn: {result}")
        return wasON

    def powerOff(self) -> bool:
        wasON = self.getState()
        result = self.executeCECCommand(f"standby {self.tv}")
        self.dbgPrint(f"powerOff: {result}")
        return wasON

    def getState(self) -> bool:
        result = self.executeCECCommand(f"pow {self.tv}")
        self.dbgPrint(f"powerState: {result}")

        if "power status: on" in result:
            return True

        if "power status: standby" in result:
            return False

        return False

    def setState(self, state: bool) -> bool:
        if state:
            # state ON
            return self.powerOn()

        # state OFF
        return self.powerOff()

    def restoreState(self, state: bool) -> bool:
        return self.setState(state)

    def executeCECCommand(self, cecCommand: str) -> str:
        shellCommand = ["cec-client", "-d", "1", "-s"]

        stdin = cecCommand + '\n'
        process = subprocess.Popen(shellCommand, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        (stdout, stderr) = process.communicate(stdin.encode())
        _ = stderr
        return stdout.decode()
