import json
import re
from os import path
from typing import Optional

from backend.event.AlarmEvent import AlarmEvent
from backend.event.SourceEvent import SourceEvent
from backend.source.MessageParser import MessageParser
from backend.util.Settings import Settings


class MessageParserMail(MessageParser):

    def __init__(self, instanceName: str, settings: Settings) -> None:
        super().__init__("ttp", instanceName, settings)
        template = open(path.join("misc/mail_templates/", self.getSettingString("template", "") + ".json"), "r").read()
        self.__template = json.loads(template)

    def parseMessage(self, sourceEvent: SourceEvent, lastEvent: Optional[SourceEvent]) -> Optional[SourceEvent]:
        alarmEvent = AlarmEvent.fromSourceEvent(sourceEvent)
        for regex in self.__template['regexes'].items():
            tmp = ""
            r = re.search(regex[1], sourceEvent.raw)
            if r is not None:
                for value in r.groups():
                    if tmp == '':
                        tmp = value
                    else:
                        tmp += ' ' + value
                alarmEvent.__setattr__(regex[0], tmp)

        alarmEvent.flags = AlarmEvent.FLAGS_VALID
        return alarmEvent
