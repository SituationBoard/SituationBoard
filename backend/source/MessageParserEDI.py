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
import json

from typing import Optional, Tuple

from backend.util.Settings import Settings
from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent
from backend.source.MessageParser import MessageParser

#TODO: add documentation for plugin

#TODO: allow merging of events from different sources

class MessageParserEDI(MessageParser):

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__("edi", instanceName, settings)
        self.__gaussKruegerZone = self.getSettingInt("gauss_krueger_zone", 4)

    def __gaussKruegerToUTMCoordinates(self, gkZone: int, gkX: float, fkY: float) -> Tuple[float, float]:
        # proj_wgs84 = pyproj.Proj(init="epsg:4326")
        # proj_gk4 = pyproj.Proj(init="epsg:31468")
        # x, y = pyproj.transform(proj_wgs84, proj_gk4, lon, lat)
        return (0.0, 0.0)

    def parseMessage(self, sourceEvent: SourceEvent, lastEvent: Optional[SourceEvent]) -> Optional[SourceEvent]:
        alarmEvent = sourceEvent

        try:
            self.print(sourceEvent.raw)

            self.print("parsing...")
            alarmData = json.loads(sourceEvent.raw, encoding="utf-8")
            missionData = alarmData["Mission"]
            self.print("done.")

            self.print(alarmData)

            alarmEvent = AlarmEvent.fromSourceEvent(sourceEvent)

            # moment = datetime.datetime.fromisoformat(missionData["AlarmDate"])
            moment = datetime.datetime.strptime(missionData["AlarmDate"], "%Y-%m-%dT%H:%M:%SZ")
            ats = moment.strftime(AlarmEvent.TIMESTAMP_FORMAT)

            alarmEvent.event = missionData["EinsatztypName"]    #TODO: use ["Stichwörter"][i]["Name"] instead ?!?
            alarmEvent.eventDetails = missionData["Schlagwort"]

            alarmEvent.location = "Test Location"               #TODO: retrieve location from JSON
            alarmEvent.locationDetails = "Test LocationDetails" #TODO: retrieve locationDetails from JSON

            alarmEvent.comment = missionData["Freitext"]

            (lat, long) = self.__gaussKruegerToUTMCoordinates(self.__gaussKruegerZone, missionData["EoX"], missionData["EoY"])
            alarmEvent.locationLatitude = lat
            alarmEvent.locationLongitude = long

            alarmEvent.alarmTimestamp = ats

            #TODO: handle status updates vs. actual alarms (and create a new flag for it)

            alarmEvent.flags = AlarmEvent.FLAGS_VALID           #TODO: only set valid if all infos are available

            self.error("Received alarm message (valid)")
        except Exception as ex:
            #TODO: return AlarmEvent with INVALID flag instead (to log them) ?!?
            self.print("failed.")
            self.print(f"Exception: {ex}")
            self.error("Received alarm message (invalid)")

        return alarmEvent
