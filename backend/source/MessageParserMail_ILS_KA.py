import json
import re
from os import path
from typing import Optional
import email

from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent
from backend.source.MessageParser import MessageParser
from backend.util.Settings import Settings


def search_regex(payload, regex) -> str:
    r = re.search(regex, payload.replace('\r\n', '\n'), flags=re.MULTILINE)
    try:
        if r is not None:
            return r[1]
        else:
            return ""
    except IndexError:
        return ""


class MessageParserMail(MessageParser):

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__('ILS-KA', instanceName, settings, multipleInstances=True)
        self.source = None

    def parseMessage(self, sourceEvent: SourceEvent, lastEvent: Optional[SourceEvent]) -> Optional[SourceEvent]:
        self.source = sourceEvent

        street = self.__search_payload(r'^[\t ]+Straße[\t ]+:[\t ]+([\w ]+)$')
        keyword = self.__search_payload(r'^[\t ]+Stichwort[\t ]+:[\t ]+([/\w\t ]*)$')
        heading = self.__search_payload(r'^[\t ]+Schlagwort[\t ]+:[\t ]+([\w -]+)$')
        city = self.__search_payload(r'^[\t ]+Ort[\t ]+:[\t ]+([\w -]+)$')
        district = self.__search_payload(r'^[\t ]+Ortsteil[\t ]+:[\t ]*([\w\t ]*)$')
        building = self.__search_payload(r'^[\t ]+Objekt[\t ]+:[\t ]*([\w\t ]*)$')
        lat = self.__search_payload(r'^https://www\.google\.de/maps/place/(\d+\.\d+),\d+\.\d+$')
        long = self.__search_payload(r'^https://www\.google\.de/maps/place/\d+\.\d+,(\d+\.\d+)$')
        comment_payload = self.__search_payload(r'^[\t ]+-+[\t ]+BEMERKUNG[\t ]+-+\n+[\t \n]([\w\s:#,.]+)-+[\t ]+Alarmmail')
        comment_filtered = filter(lambda x: not re.match(r'^\n*$', x), comment_payload)
        comment = ''.join(comment_filtered)

        alarm_event = AlarmEvent.fromSourceEvent(sourceEvent)
        alarm_event.event = heading
        alarm_event.eventDetails = keyword
        event_location = ''
        if district:
            event_location += district
        if district and city:
            event_location += " ,"
        if city:
            event_location += city
        alarm_event.location = event_location
        event_location_details = ''
        if street:
            event_location_details += street
        if street and building:
            event_location_details += "\n"
        if building:
            event_location += "Objekt: {}".format(building)
        alarm_event.locationDetails = event_location_details
        alarm_event.locationLatitude = lat
        alarm_event.locationLongitude = long
        alarm_event.comment = comment

        alarm_event.flags = AlarmEvent.FLAGS_VALID
        return alarm_event

    def __search_payload(self, regex: str) -> str:
        return search_regex(self.source.raw, regex)
