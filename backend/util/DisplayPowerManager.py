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

from typing import List, Tuple, Optional

from backend.util.Module import Module
from backend.util.Settings import Settings

class DisplayPowerManager(Module):
    """The DisplayPowerManager (together with DisplayDevice) controls the power state of the attached display (e.g. TV screen) via CEC.
    It allows the ActivateScreen action to wake the display from standby mode in case of an alarm event."""

    DEFAULT_TIMEOUT = 10
    DEFAULT_TIMEOUT_SCAN = 20
    DEFAULT_TIMEOUT_LIST = 20

    def __init__(self, settings: Settings) -> None:
        super().__init__("cec", settings = None, debug = settings.getBackendDebug())

    def getDevice(self, cecDevice: str = "", deviceID: int = 0, commandTimeout: int = DEFAULT_TIMEOUT) -> "DisplayDevice":
        device = DisplayDevice(self, cecDevice, deviceID, commandTimeout)
        return device

    def scanDevices(self, cecDevice: str = "", commandTimeout: int = DEFAULT_TIMEOUT_SCAN) -> str:
        _, output = self.executeCECCommand("scan", cecDevice, commandTimeout)
        return output

    def listCECDevices(self, commandTimeout: int = DEFAULT_TIMEOUT_LIST) -> str:
        shellCommand = ["cec-client", "--list-devices"]
        _, output = self.__executeCommand(shellCommand, "", commandTimeout)
        return output

    def executeCECCommand(self, cecCommand: str, cecDevice: str = "", timeoutSeconds: int = DEFAULT_TIMEOUT) -> Tuple[int, str]:
        if cecDevice != "":
            shellCommand = ["cec-client", cecDevice, "--log-level", "1", "--single-command"]
        else:
            shellCommand = ["cec-client", "--log-level", "1", "--single-command"]
        return self.__executeCommand(shellCommand, cecCommand, timeoutSeconds)

    def __executeCommand(self, shellCommand: List[str], stdinCommand: str = "", timeoutSeconds: int = DEFAULT_TIMEOUT) -> Tuple[int, str]:
        if stdinCommand != "":
            stdin = stdinCommand + '\n'
        else:
            stdin = ""

        if self.isDebug():
            shellCmd = " ".join(shellCommand)
            self.dbgPrint(f"Command: {shellCmd}")
            self.dbgPrint(f"Input:   {stdinCommand}")

        try:
            with subprocess.Popen(shellCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE) as process:
                (stdout, stderr) = process.communicate(stdin.encode(), timeout=timeoutSeconds)
                _ = stderr # stderr is redirected to stdout
                output = stdout.decode()
                exitStatus = process.returncode

                if self.isDebug():
                    self.dbgPrint(f"Output:  {output}")
                    self.dbgPrint(f"Result:  {exitStatus}")

                return exitStatus, output

        except Exception as e:
            self.error(f"Command execution failed ({e})")
            return 42, f"{e}"

class DisplayDevice:
    """A DisplayDevice represents a specific display device that is controlled via the DisplayPowerManager and CEC."""

    def __init__(self, displayPowerManager: DisplayPowerManager, cecDevice: str = "", deviceID: int = 0, commandTimeout: int = DisplayPowerManager.DEFAULT_TIMEOUT):
        self.__dpm = displayPowerManager
        self.__cecDevice = cecDevice
        self.__deviceID = deviceID
        self.__commandTimeout = commandTimeout

    def __executeCECCommand(self, cecCommand: str) -> Tuple[int, str]:
        fullCommand = f"{cecCommand} {self.__deviceID}"
        return self.__dpm.executeCECCommand(fullCommand, self.__cecDevice, self.__commandTimeout)

    def powerOn(self) -> bool:
        result, _ = self.__executeCECCommand("on")
        if result == 0:
            return True
        return False

    def powerOff(self) -> bool:
        result, _ = self.__executeCECCommand("standby")
        if result == 0:
            return True
        return False

    def getPowerState(self) -> Optional[bool]:
        result, output = self.__executeCECCommand("pow")
        if result == 0:
            if "power status: on" in output:
                return True
            if "power status: standby" in output:
                return False
        return None

    def setPowerState(self, state: bool) -> bool:
        if state:
            return self.powerOn()
        return self.powerOff()
