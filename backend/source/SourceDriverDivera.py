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

import http
import json
import string
import datetime

from typing import Optional, Tuple

from test.DiveraMockAPI import DiveraMockAPI

import requests

from backend.source.SourceDriver import SourceDriver, SourceState
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SettingEvent import SettingEvent
from backend.util.Settings import Settings

class SourceDriverDivera(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings, lastAlarmEvent: Optional[AlarmEvent] = None, mockAPI: Optional[DiveraMockAPI] = None) -> None:
        super().__init__("divera", instanceName, settings)
        self.__mockAPI = mockAPI # passed by test cases (for automated testing only)
        self.__apiKey = self.getSettingString("api_key", "")
        self.__timeout = self.getSettingInt("timeout", 5)
        self.__apiURL = self.getSettingString("api_url", "https://www.divera247.com") # adjustable for test purposes
        self.__useMockAPI = self.getSettingBoolean("use_mock_api", False) # simulate events with mock API instead of regular API (during normal exectution)
        self.__ignoreTestAlarm = self.getSettingBoolean("ignore_test_alarm", False)

        self.__showVehicleStatus = self.getSettingBoolean("show_vehicle_status", True)
        self.__showCrewResponses = self.getSettingBoolean("show_crew_responses", True)

        self.__responseIDFast = self.getSettingString("response_id_fast", "99148") # available in < 5 min
        self.__responseIDSlow = self.getSettingString("response_id_slow", "99149") # available in < 10 min
        self.__responseIDNA = self.getSettingString("response_id_na", "99150")     # not available

        if self.__mockAPI is None and self.__useMockAPI:
            apiPort = DiveraMockAPI.DEFAULT_API_PORT
            apiHost = DiveraMockAPI.DEFAULT_API_HOST
            self.__apiURL = f"http://{apiHost}:{apiPort}"
            self.__apiKey = DiveraMockAPI.DEFAULT_API_KEY
            self.__mockAPI = DiveraMockAPI(self.__apiKey)
            self.__mockAPI.run(apiHost, apiPort, interactive=True)

        if self.__apiURL == "":
            self.fatal("api_url not configured")

        if self.__apiKey == "":
            self.fatal("api_key not configured")

        self.__lastAlarmEvent: Optional[AlarmEvent] = lastAlarmEvent
        self.__lastSettingEvent: Optional[SettingEvent] = None
        self.__lastSourceState: Optional[SourceState] = None

    def testSetAPIURL(self, newURL: str) -> None: # should only be called by automated tests
        self.__apiURL = newURL

    def testResetSourceState(self, lastAlarmEvent: Optional[AlarmEvent] = None) -> None: # should only be called by automated tests
        self.__lastAlarmEvent = lastAlarmEvent
        self.__lastSettingEvent = None
        self.__lastSourceState = None

    def __retrieveAlarmEvent(self) -> Tuple[Optional[AlarmEvent], bool]: #pylint: disable=too-many-return-statements
        try:
            response = requests.get(self.__apiURL + "/api/last-alarm", params={"accesskey": self.__apiKey}, timeout=self.__timeout)
        except Exception as e:
            self.error(f"failed to retrieve last alarm event ({e})")
            return None, False

        if response.status_code != http.HTTPStatus.OK:
            self.error(f"failed to retrieve last alarm (status code {response.status_code})")
            return None, False

        try:
            jsonResult = response.json()
            rawResult = response.text
            self.dbgPrint(rawResult)

            if jsonResult is None or jsonResult["success"] is False or "data" not in jsonResult:
                self.dbgPrint("no alarm event available")
                return None, True

            data = jsonResult["data"]

            # handle closed alarms
            if data["ts_close"] != 0:
                self.dbgPrint("alarm event is already closed")
                return None, True

            # handle test alarms
            if self.__ignoreTestAlarm:
                if data["author_id"] == 0:
                    self.dbgPrint("ignored test alarm")
                    return None, True

            alarmEvent = AlarmEvent()

            # handle alarm udpates if required
            if self.__lastAlarmEvent is not None:
                diveraNewEventID = data["id"]
                diveraNewUpdateTS = data["ts_update"]
                lastAlarmEventRaw = json.loads(self.__lastAlarmEvent.raw)
                lastAlarmEventData = lastAlarmEventRaw["data"]
                diveraLastEventID = lastAlarmEventData["id"]
                diveraLastUpdateTS = lastAlarmEventData["ts_update"]
                if diveraNewEventID == diveraLastEventID:
                    if diveraNewUpdateTS > diveraLastUpdateTS:
                        self.clrPrint(f"Updating changed alarm event #{self.__lastAlarmEvent.eventID}")
                        alarmEvent = self.__lastAlarmEvent
                    else:
                        self.dbgPrint("ignoring unchanged alarm event")
                        return None, True

            if alarmEvent is not self.__lastAlarmEvent:
                self.clrPrint("Handling new alarm event")
                alarmEvent.timestamp = datetime.datetime.now().strftime(AlarmEvent.TIMESTAMP_FORMAT)

            # actually fill alarm event with details
            alarmEvent.source = SourceEvent.SOURCE_DIVERA
            alarmEvent.sender = self.__apiURL
            alarmEvent.flags = AlarmEvent.FLAGS_VALID
            alarmEvent.raw = rawResult

            aTimestamp = data["ts_create"]
            ats = datetime.datetime.fromtimestamp(aTimestamp)
            alarmEvent.alarmTimestamp = ats.strftime(AlarmEvent.TIMESTAMP_FORMAT)

            # split title field into event and eventDetails
            aEventComplete = data["title"]
            aEventStripped = aEventComplete.strip(string.whitespace)
            aEventParts = aEventStripped.split(" #", 2)
            if len(aEventParts) < 2:
                alarmEvent.event = aEventParts[0].strip()
                alarmEvent.eventDetails = ""
            else:
                alarmEvent.event = aEventParts[0].strip()
                alarmEvent.eventDetails = "#" + aEventParts[1].strip()

            priority = data["priority"]
            if priority:
                pass # alarmEvent.event = alarmEvent.event + " (Prio)"
            else:
                alarmEvent.event = alarmEvent.event + " (keine Prio)"

            # split address field into location and locationDetails
            aLocationComplete = data["address"]
            aLocationStripped = aLocationComplete.strip(string.whitespace + ",")
            aLocationParts = aLocationStripped.split(",", 2)
            if len(aLocationParts) < 2:
                aLocationParts = aLocationStripped.split("  ", 2)
            if len(aLocationParts) < 2:
                alarmEvent.location = "" # avoid showing confidential information (e.g., in the event list)
                alarmEvent.locationDetails = aLocationParts[0].strip()
            else:
                alarmEvent.location = aLocationParts[1].strip()
                alarmEvent.locationDetails = aLocationParts[0].strip()

            alarmEvent.locationLatitude = data["lat"]
            alarmEvent.locationLongitude = data["lng"]

            description = data["text"]

            # create line with crew responses and append it to the comment field
            crewResponses = ""
            if self.__showCrewResponses:
                readCount = data["count_read"]
                recipientCount = data["count_recipients"]
                respCountFast = 0 if self.__responseIDFast not in data["ucr_answeredcount"] else data["ucr_answeredcount"][self.__responseIDFast]
                respCountSlow = 0 if self.__responseIDSlow not in data["ucr_answeredcount"] else data["ucr_answeredcount"][self.__responseIDSlow]
                respCountNA = 0 if self.__responseIDNA not in data["ucr_answeredcount"] else data["ucr_answeredcount"][self.__responseIDNA]
                # priority = data["priority"]
                # crewResponses = f"{readCount}/{recipientCount} >> fast: {respCountFast} – slow: {respCountSlow} – n/a: {respCountNA}"
                # if priority:
                #     crewResponses = "PRIO " + crewResponses
                SPACE = "    "
                crewResponses = f"✅ {respCountFast}{SPACE}⏳ {respCountSlow}{SPACE}❌ {respCountNA}{SPACE}👁️ {readCount}/{recipientCount}"


            if description != "" and crewResponses != "":
                alarmEvent.comment = f"{description}\n\n{crewResponses}"
            else:
                alarmEvent.comment = f"{description}{crewResponses}"

            self.__lastAlarmEvent = alarmEvent
            return alarmEvent, True
        except Exception as e:
            self.error(f"failed to handle last alarm event ({e})")

        return None, False

    def __createSettingEventIfRequired(self, rawResult: str = "", statusLine: str = "", latestChange: int = 0) -> Optional[SettingEvent]:
        if latestChange == 0:
            now = datetime.datetime.now()
            timestampChanged = now.strftime(AlarmEvent.TIMESTAMP_FORMAT)
        else:
            lcts = datetime.datetime.fromtimestamp(latestChange)
            timestampChanged = lcts.strftime(SettingEvent.TIMESTAMP_FORMAT)

        # send SettingEvents for status updates with a different and even with the same status,
        # but avoid sending empty SettingEvents over and over again (e.g., in case of a failure)
        if self.__lastSettingEvent is not None and \
        self.__lastSettingEvent.value == statusLine and \
        (self.__lastSettingEvent.timestamp == timestampChanged or statusLine == ""):
            self.dbgPrint("ignoring unchanged vehicle status")
            return None

        settingEvent = SettingEvent()

        settingEvent.timestamp = timestampChanged
        settingEvent.source = SourceEvent.SOURCE_DIVERA
        settingEvent.sender = self.__apiURL
        settingEvent.flags = SettingEvent.FLAGS_VALID
        settingEvent.raw = rawResult

        settingEvent.key = "news"
        settingEvent.value = statusLine

        self.clrPrint("Updating vehicle status")
        self.__lastSettingEvent = settingEvent
        return settingEvent

    def __retrieveVehicleStatus(self) -> Tuple[Optional[SettingEvent], bool]:
        try:
            response = requests.get(self.__apiURL + "/api/v2/pull/vehicle-status", params={"accesskey": self.__apiKey}, timeout=self.__timeout)
        except Exception as e:
            self.error(f"failed to retrieve vehicle status ({e})")
            settingEvent = self.__createSettingEventIfRequired() # make sure we send a SettingEvent to reset/hide the current vehicle status
            return settingEvent, False

        if response.status_code != http.HTTPStatus.OK:
            self.error(f"failed to retrieve vehicle status (status code {response.status_code})")
            settingEvent = self.__createSettingEventIfRequired() # make sure we send a SettingEvent to reset/hide the current vehicle status
            return settingEvent, False

        try:
            jsonResult = response.json()
            rawResult = response.text
            self.dbgPrint(rawResult)

            if jsonResult is None or jsonResult["success"] is False or "data" not in jsonResult:
                self.error("no vehicle status available")
                settingEvent = self.__createSettingEventIfRequired(rawResult) # make sure we send a SettingEvent to reset/hide the current vehicle status
                return settingEvent, False

            data = jsonResult["data"]

            statusLine = ""
            latestChange = 0
            for vehicle in data:
                vehicleShortname = vehicle['shortname']
                vehicleName = vehicle['name']
                vehicleStatus = vehicle['fmsstatus']
                timestampChange = vehicle['fmsstatus_ts']

                status = f"{vehicleShortname} {vehicleName}: Status {vehicleStatus}"
                if statusLine == "":
                    statusLine = status
                else:
                    statusLine = f"{statusLine}  –  {status}"

                latestChange = max(latestChange, timestampChange)

            settingEvent = self.__createSettingEventIfRequired(rawResult, statusLine, latestChange) # send a SettingEvent if a status was updated
            return settingEvent, True
        except Exception as e:
            self.error(f"failed to handle vehicle status ({e})")
            settingEvent = self.__createSettingEventIfRequired() # make sure we send a SettingEvent to reset/hide the current vehicle status
            return settingEvent, False

    def retrieveEvent(self) -> Optional[SourceEvent]:
        success = True
        sourceEvent: Optional[SourceEvent] = None

        alarmEvent, alarmSuccess = self.__retrieveAlarmEvent()
        if not alarmSuccess:
            success = False
        if alarmEvent is not None:
            sourceEvent = alarmEvent

        if sourceEvent is None and self.__showVehicleStatus:
            settingEvent, settingSuccess = self.__retrieveVehicleStatus()
            if not settingSuccess:
                success = False
            if settingEvent is not None:
                sourceEvent = settingEvent

        if success:
            self.__lastSourceState = SourceState.OK
        else:
            self.__lastSourceState = SourceState.ERROR

        return sourceEvent

    def getSourceState(self) -> SourceState:
        if self.__lastSourceState is None:
            return SourceState(SourceState.ERROR)

        return self.__lastSourceState
