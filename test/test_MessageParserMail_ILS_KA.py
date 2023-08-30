import os
import json
import shutil
import datetime
import uuid

from email.utils import format_datetime
from backend.util.AppInfo import AppInfo
from backend.util.Settings import Settings
from backend.source.MessageParserMail_ILS_KA import MessageParserMail
from backend.event.SourceEvent import SourceEvent
from backend.event.AlarmEvent import AlarmEvent


def pytest_generate_tests(metafunc):
    appInfo = AppInfo()
    idlist = []
    argvalues = []
    argnames = ['input', 'result', 'parser']
    input_dir = os.path.join(appInfo.path, "test/parser_input/ILS-KA")
    s = get_settings()
    parser = MessageParserMail(instanceName=str(uuid.uuid1()), settings=s)
    for file in os.listdir(input_dir):
        args = []
        if os.path.isdir(input_dir):
            mail_file_path = os.path.join(input_dir, file, "mail.txt")
            result_file_path = os.path.join(input_dir, file, "result.json")
            if os.path.isfile(mail_file_path) and os.path.isfile(result_file_path):
                input = open(mail_file_path, "r").read()
                try:
                    result = json.loads(open(result_file_path, 'r').read())
                except json.decoder.JSONDecodeError:
                    result = None
                if result is not None and input is not None:
                    idlist.append(file)
                    args.append(input)
                    args.append(result)
                    args.append(parser)
                    argvalues.append(args)
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


def get_settings():
    appInfo = AppInfo()
    settingsFilenameOrig = os.path.join(appInfo.path, "misc/setup/situationboard_default.conf")
    settingsFilename = os.path.join(appInfo.path, ".temp/situationboard.conf")
    shutil.copy(settingsFilenameOrig, settingsFilename)
    return Settings(settingsFilename, appInfo.path)


class Test_MessageParserMail:

    def __make_source_event(self, input):
        sourceEvent = SourceEvent()
        sourceEvent.source = SourceEvent.SOURCE_MAIL
        sourceEvent.timestamp = format_datetime(datetime.datetime.now())
        sourceEvent.sender = "test@tests.local"
        sourceEvent.raw = input
        return sourceEvent

    def test_parse_event(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.event == result['result']['event']

    def test_parse_eventDetails(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.eventDetails == result['result']['eventDetails']

    def test_parse_Location(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.location == result['result']['location']

    def test_parse_LocationDetails(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.locationDetails == result['result']['locationDetails']

    def test_parte_LocationLatitude(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.locationLatitude == result['result']['locationLatitude']

    def test_parte_LocationLongitude(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.locationLongitude == result['result']['locationLongitude']

    def test_parte_Comment(self, input, result, parser):
        t = parser.parseMessage(self.__make_source_event(input), None)
        assert t.comment == result['result']['comment']
