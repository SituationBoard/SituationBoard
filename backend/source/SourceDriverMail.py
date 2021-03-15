import email
import ssl
from email.utils import parseaddr
from email import policy
from socket import gaierror
from typing import Optional

from imapclient import IMAPClient
from imapclient.exceptions import LoginError

from backend.event.SourceEvent import SourceEvent
from backend.source.MessageParser import MessageParser
from backend.source.SourceDriver import SourceDriver, SourceState
from backend.util.Settings import Settings


class SourceDriverMail(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings, parser: MessageParser) -> None:
        super().__init__("mail", instanceName, settings, parser)
        self.__allowlist = self.getSettingList("allowlist", [])
        self.__denylist = self.getSettingList("denylist", [])
        self.__connected = False

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  #Workaround for test
        context.set_ciphers('DEFAULT@SECLEVEL=1')  #Workaround for test
        try:
            self.__imap_server = IMAPClient(self.getSettingString("mail_server", "blubb.test"), use_uid=True,ssl_context=context)
        except gaierror:
            self.error("Failed to connect to Mail Server")
        else:
            try:
                self.__imap_server.login(self.getSettingString("mail_user", ""), self.getSettingString("mail_password", ""))
            except LoginError:
                self.error("Mail Server login failed")
            else:
                self.__connected = True
                self.__imap_server.select_folder('INBOX',readonly=False)

    def retrieveEvent(self) -> Optional[SourceEvent]:
        if self.__connected:
            messages = self.__imap_server.search('UNSEEN')
            for _, message_data in self.__imap_server.fetch(messages, "RFC822").items():
                message = email.message_from_bytes(message_data[b"RFC822"], policy=policy.default)
                sender = parseaddr(message.get("From"))[1]
                if self.isSenderAllowed(allowlist=self.__allowlist, denylist=self.__denylist, sender=sender):
                    sourceEvent = SourceEvent()
                    sourceEvent.source = SourceEvent.SOURCE_MAIL
                    sourceEvent.timestamp = message.get('Date')
                    sourceEvent.sender = sender
                    sourceEvent.raw = message.get_body('plain').get_payload()  # type: ignore[attr-defined]
                    parsedSourceEvent = self.parser.parseMessage(sourceEvent, None)  # type: ignore[union-attr]
                    return parsedSourceEvent
        return None

    def getSourceState(self) -> SourceState:
        if self.__connected:
            return SourceState.OK
        return SourceState.ERROR
