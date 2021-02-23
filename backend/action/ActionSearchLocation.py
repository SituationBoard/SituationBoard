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

from geopy.geocoders import Nominatim

from backend.action.Action import Action
from backend.util.Settings import Settings
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent

class ActionSearchLocation(Action):

    def __init__(self, instanceName: str, settings: Settings):
        super().__init__("search_location", instanceName, settings)
        self.__timeout = self.getSettingInt("timeout", 5)

    def handleEvent(self, sourceEvent: SourceEvent) -> None:
        if isinstance(sourceEvent, AlarmEvent):
            alarmEvent = sourceEvent

            if alarmEvent.invalid:
                return

            if alarmEvent.locationLatitude == 0.0 and alarmEvent.locationLongitude == 0.0:
                if alarmEvent.location != "" and alarmEvent.locationDetails != "":
                    address = alarmEvent.location + " " + alarmEvent.locationDetails
                    try:
                        geoLocator = Nominatim(user_agent="SB", timeout=self.__timeout)
                        self.dbgPrint(f"Searching address: {address}")
                        location = geoLocator.geocode(address)
                        if location is not None:
                            self.dbgPrint(f"Found address: {location.address}")
                            self.dbgPrint(f"Found location: latitude={location.latitude} longitude={location.longitude}")
                            #self.dbgPrint(location.raw)

                            alarmEvent.locationLatitude = location.latitude
                            alarmEvent.locationLongitude = location.longitude
                        else:
                            self.error("Failed to search location")

                    except Exception:
                        self.error("Failed to search location")
