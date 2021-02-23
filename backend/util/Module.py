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

import sys
import traceback

from typing import Optional, NoReturn, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.util.Settings import Settings #pylint: disable=cyclic-import

class Module:
    """Module is the base class of many subsystems and plugins of the backend.
    It offers methods to output log, debug and error messages.
    Modules have a name that is prepended to all those messages."""

    PLAIN_TEXT_OUTPUT = False

    OUTPUT_RESET  = "\u001b[0m"  # regular output

    OUTPUT_BOLD   = "\u001b[1m"  # bold/bright
    OUTPUT_UNDER  = "\u001b[4m"  # underlined

    OUTPUT_RED    = "\u001b[31m" # fatal error
    OUTPUT_GREEN  = "\u001b[32m" # important messages (startup, alarm, ...)
    OUTPUT_YELLOW = "\u001b[33m" # error
    OUTPUT_BLUE   = "\u001b[34m" # debug output

    def __init__(self, moduleName: str, settings: Optional['Settings'] = None, debug: bool = False) -> None:
        """Constructs a Module with a unique module name and optional access to settings and initializes it.

        :param moduleName: string representing the unique module name
        :param settings: reference to the Settings object (optional)
        :param debug: bool whether debug mode is active (used only when Settings are not available)"""
        self.moduleName = moduleName
        self.moduleSettings = settings
        self.moduleDebug = debug

    def lateInit(self, settings: Optional['Settings'] = None, debug: bool = False) -> None:
        self.moduleSettings = settings
        self.moduleDebug = debug

    def __str__(self) -> str:
        return self.moduleName

    def __repr__(self) -> str:
        return self.moduleName

    def __printMessage(self, message: str, style: str = "", error: bool = False) -> None:
        if message == "":
            return

        if Module.PLAIN_TEXT_OUTPUT:
            if error:
                smnUpper = self.moduleName.upper()
                print(f"{smnUpper}! {message}", file=sys.stderr)
            else:
                smnLower = self.moduleName.lower()
                print(f"{smnLower}: {message}", flush=True)
        else:
            if style != "":
                styleOn  = style
                styleOff = Module.OUTPUT_RESET
            else:
                styleOn  = ""
                styleOff = ""

            smn = self.moduleName

            modStyleOn  = Module.OUTPUT_BOLD
            modStyleOff = Module.OUTPUT_RESET
            if error:
                print(f"{modStyleOn}{smn}:{modStyleOff} {styleOn}{message}{styleOff}", file=sys.stderr)
            else:
                print(f"{modStyleOn}{smn}:{modStyleOff} {styleOn}{message}{styleOff}", flush=True)

    def __printException(self, exception: Optional[Exception], style: str = "") -> None:
        if exception is None:
            return

        if Module.PLAIN_TEXT_OUTPUT:
            print(f"{exception}", file=sys.stderr)
        else:
            if style != "":
                styleOn  = style
                styleOff = Module.OUTPUT_RESET
            else:
                styleOn  = ""
                styleOff = ""

            exceptionInfo = traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__)
            exceptionText = "".join(exceptionInfo)
            print(f"{styleOn}{exceptionText}{styleOff}", file=sys.stderr)

    def isDebug(self) -> bool:
        """Returns whether the module is in debug mode (True) or not (False).

        :return: bool whether debug mode is active
        """
        if self.moduleSettings is not None:
            return self.moduleSettings.getBackendDebug()

        return self.moduleDebug

    def print(self, message: str) -> None:
        """Prints regular output and prepends the module name.

        :param message: string representing the message to be printed"""
        self.__printMessage(message)

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Prints a error message of a non-fatal error (and an exception if given).

        :param message: string representing the error message to be printed
        :param exception: Exception that caused the error (optional)"""
        self.__printMessage(message, Module.OUTPUT_YELLOW, True)
        self.__printException(exception, Module.OUTPUT_YELLOW)

    def fatal(self, message: str, exception: Optional[Exception] = None, status: int = 1) -> NoReturn:
        """Prints an error message of a fatal error (and an exception if given)
        and terminates the backend with an error code.

        :param message: string representing the error message to be printed
        :param exception: Exception that caused the error (optional)
        :param status: integer with the status code of the terminating backend (optional, default 1)"""
        self.__printMessage(message, Module.OUTPUT_RED, True)
        self.__printException(exception, Module.OUTPUT_RED)
        sys.exit(status)

    def fatalContinue(self, message: str, exception: Optional[Exception] = None) -> None:
        """Prints an error message of a fatal error (and an exception if given)
        but does not terminate the backend. Instead the caller of this function is responsible to do so later on.

        :param message: string representing the error message to be printed
        :param exception: Exception that caused the error (optional)"""
        self.__printMessage(message, Module.OUTPUT_RED, True)
        self.__printException(exception, Module.OUTPUT_RED)

    def clrPrint(self, message: str) -> None:
        """Prints a highlighted message that is of some importance to the user.

        :param message: string representing the message to be printed"""
        self.__printMessage(message, Module.OUTPUT_GREEN, False)

    def dbgPrint(self, message: str) -> None:
        """Prints a debug message that is only shown if the module is in debug mode.

        :param message: string representing the debug message to be printed"""
        if self.isDebug():
            self.__printMessage(message, Module.OUTPUT_BLUE, False)
