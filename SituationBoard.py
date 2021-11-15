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
import os
import types
import time
import argparse
import signal

from typing import List, Optional

from backend.data.Database import Database
from backend.data.CSVImporter import CSVImporter
from backend.data.CSVExporter import CSVExporter
from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.util.DisplayPowerManager import DisplayPowerManager
from backend.util.PluginManager import PluginManager
from backend.util.Module import Module
from backend.api.WebSocket import WebSocket

class SituationBoardBackend(Module):
    """The SituationBoardBackend class represents the core of the backend service.
    It initializes the different subsystems and implements core application logic
    like the event loop that is responsible for retrieving and handling of alarm events."""

    def __init__(self, appInfo: AppInfo, settings: Settings, database: Database):
        super().__init__("situationboard", settings)
        self.appInfo = appInfo
        self.settings = settings
        self.database = database
        self.displayPowerManager = DisplayPowerManager(self.settings)
        self.webSocket = WebSocket(self.appInfo, self.settings, self.database)
        self.pluginManager = PluginManager(self.settings, self.database, self.webSocket, self.displayPowerManager)
        signal.signal(signal.SIGTERM, self.__shutdownHandler) # a SIGTERM signal causes the backend to shutdown
        signal.signal(signal.SIGINT, self.__shutdownHandler)  # a SIGINT signal causes the backend to shutdown
        sys.stdin.close()

    def __shutdownHandler(self, signum: int, frame: Optional[types.FrameType]) -> None: #pylint: disable=no-member
        """The __shutdownHandler handles the SIGTERM/SIGINT signal and terminates the backend."""
        self.clrPrint("Terminating backend")
        # database is committed and closed automatically (via atexit)
        sys.exit(0)

    def backgroundTask(self) -> None:
        """Background thread / event loop that retrieves SourceEvents from configured SourceDrivers
        and handles them by passing them to all the configured Action plugins.
        Those plugins in turn may perform various actions (like updating the frontend of web clients).
        When no SourceEvents are retrieved, Action plugins are allowed to perform housekeeping operations instead."""

        sleepDuration = self.settings.getBackendLoopSleepDuration()

        while True:
            # wait for alarms or setting event messages, parse them and handle them
            message = self.pluginManager.retrieveEvent()

            if message is not None:
                # handle source event by triggering all required actions / event handlers ...
                #   new alarm   -> add to database and send an async alarm event to frontend
                #   new setting -> update setting and send an async update event to frontend
                self.pluginManager.handleEvent(message)
            else:
                # perform housekeeping tasks ...
                housekeepingStart = time.time()
                self.pluginManager.handleCyclic()
                housekeepingEnd = time.time()

                # maybe sleep some time ...
                housekeepingDuration = housekeepingEnd - housekeepingStart
                if housekeepingDuration < sleepDuration:
                    remainingDuration = sleepDuration - housekeepingDuration
                    self.webSocket.sleep(round(remainingDuration))

    def run(self) -> None:
        # Read all the configured plugins from the configuration file and initialize them
        self.print("Initializing all configured plugins")
        self.pluginManager.initPlugins()

        # Initialize websocket interface and register all endpoints
        self.print("Initializing websocket interface")
        self.webSocket.init(self.pluginManager)

        # Start the background task with the event loop that retrieves events and handles them
        self.print("Starting background task")
        self.webSocket.start_background_task(self.backgroundTask)

        # Start the webserver and the websocket API for the frontend (does not return)
        self.print("Starting websocket interface")
        self.webSocket.run()


class SituationBoard(Module):
    """The SituationBoard class is the entry point of the SituationBoard application.
    It parses command line parameters, initializes the settings and the database,
    implements import/export functionality and starts the backend service (if required)."""

    DEFAULT_CONFIG_FILENAME   = "situationboard.conf"
    DEFAULT_DATABASE_FILENAME = "situationboard.sqlite"

    def __init__(self) -> None:
        """This constructor is responsible for the early startup of the backend
        and instantiates all the required modules."""
        super().__init__("situationboard", settings = None, debug = False)
        self.appInfo = AppInfo()

    def run(self, argv: List[str]) -> None:
        """This is the main entry point of the backend application."""

        defaultConfigPath   = os.path.join(self.appInfo.path, SituationBoard.DEFAULT_CONFIG_FILENAME)
        defaultConfigPath   = os.getenv("SB_CONFIG", defaultConfigPath)

        defaultDatabasePath = os.path.join(self.appInfo.path, SituationBoard.DEFAULT_DATABASE_FILENAME)
        defaultDatabasePath = os.getenv("SB_DATABASE", defaultDatabasePath)

        parser = argparse.ArgumentParser(description=f"{self.appInfo.name} v{self.appInfo.version}", add_help=False)
        igroup = parser.add_argument_group("Important Commands and Parameters")
        mmutex = igroup.add_mutually_exclusive_group()
        mmutex.add_argument("-s", "--server",   help="start backend server (default)",  default=True,                action='store_true')
        mmutex.add_argument("-i", "--import",   help="import data from CSV",            default=None,                dest='importFile')
        mmutex.add_argument("-e", "--export",   help="export data to CSV",              default=None,                dest='exportFile')
        mmutex.add_argument("-n", "--version",  help="show version number and exit",    default=False,               action='store_true')
        mmutex.add_argument("-h", "--help",     help="show this help message and exit",                              action='help')
        ogroup = parser.add_argument_group("Other Parameters and Options")
        ogroup.add_argument("-c", "--config",   help="alternate path to config file",   default=defaultConfigPath,   dest='configPath')
        ogroup.add_argument("-d", "--database", help="alternate path to database file", default=defaultDatabasePath, dest='databasePath')
        ogroup.add_argument("-r", "--reset",    help="reset database before import",    default=False,               action='store_true')
        ogroup.add_argument("-v", "--verbose",  help="force debug output",              default=False,               action='store_true')

        # args = parser.parse_args(argv)
        args = parser.parse_args()

        # Check command line parameters
        if (args.reset is True) and (args.importFile is None):
            parser.error("reset is only allowed for the import command")
            sys.exit(1)

        # Show version number and exit (if requested)
        if args.version:
            print(f"{self.appInfo.name} {self.appInfo.version}")
            sys.exit(0)

        # Print application header
        if args.importFile is not None:
            self.print("Starting import from CSV...")
        elif args.exportFile is not None:
            self.print("Starting export to CSV...")
        else:
            self.clrPrint(f"Starting {self.appInfo.name} backend v{self.appInfo.version} (PID {self.appInfo.pid})")

        # Load configuration and database
        settings = Settings(args.configPath, self.appInfo.path, args.verbose)
        database = Database(args.databasePath, args.reset)
        self.lateInit(settings)

        # Handle CSV import/export (if required)
        if args.importFile is not None:
            csvImporter = CSVImporter(database)
            result = csvImporter.importEvents(args.importFile)
            sys.exit(result)
        elif args.exportFile is not None:
            csvExporter = CSVExporter(database)
            result = csvExporter.exportEvents(args.exportFile)
            sys.exit(result)

        # Start SituationBoard backend service
        backendService = SituationBoardBackend(self.appInfo, settings, database)
        backendService.run()


def main(argv: List[str]) -> None:
    situationBoard = SituationBoard()
    situationBoard.run(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
