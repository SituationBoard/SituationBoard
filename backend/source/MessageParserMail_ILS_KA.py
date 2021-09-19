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
        alarmEvent = AlarmEvent.fromSourceEvent(sourceEvent)
        alarmEvent.event = self.__search_payload(r'^[\t ]+Schlagwort[\t ]+:[\t ]+([\w -]+)$')
        alarmEvent.eventDetails = self.__search_payload(r'^[\t ]+Stichwort[\t ]+:[\t ]+([/\w\t ]*)$')
        alarmEvent.location =  self.__search_payload(r'^[\t ]+Ortsteil[\t ]+:[\t ]*([\w\t ]*)$') + " ," + self.__search_payload(r'^[\t ]+Ort[\t ]+:[\t ]+([\w -]+)$')
        alarmEvent.locationDetails = self.__search_payload(r'^[\t ]Straße[\t ]+:[\t ]+([\w ]+)$') + "\nObjekt: " + self.__search_payload(r'^[\t ]+Objekt[\t ]+:[\t ]*([\w\t ]*)$')
        alarmEvent.locationLatitude = self.__search_payload(r'^https://www\.google\.de/maps/place/(\d+\.\d+),\d+\.\d+$')
        alarmEvent.locationLongitude = self.__search_payload(r'^https://www\.google\.de/maps/place/\d+\.\d+,(\d+\.\d+)$')
        alarmEvent.comment = self.__search_payload(r'^[\t ]+-+[\t ]+BEMERKUNG[\t ]+-+\n+[\t ]([\w\s:#]+)-+[\t ]+Alarmmail')

        alarmEvent.flags = AlarmEvent.FLAGS_VALID
        return alarmEvent

    def __search_payload(self, regex: str) -> str:
        return search_regex(self.source.raw, regex)
