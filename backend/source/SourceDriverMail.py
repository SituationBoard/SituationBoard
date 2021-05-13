import email
import ssl
from email import policy
from email.utils import parseaddr
from socket import gaierror, timeout
from typing import Optional

from imapclient import IMAPClient
from imapclient.exceptions import LoginError

from backend.event.SourceEvent import SourceEvent
from backend.event.UnhandledEvent import UnhandledEvent
from backend.source.MessageParser import MessageParser
from backend.source.SourceDriver import SourceDriver, SourceState
from backend.util.Settings import Settings


class SourceDriverMail(SourceDriver):

    def __init__(self, instanceName: str, settings: Settings, parser: MessageParser) -> None:
        super().__init__("mail", instanceName, settings, parser)
        self.__settings = settings
        self.__allowlist = self.getSettingList("allowlist", [])
        self.__denylist = self.getSettingList("denylist", [])
        self.__connect()

    def retrieveEvent(self) -> Optional[SourceEvent]:
        try:
            if self.isDebug():
                self.print("Checking for new mails")
            messages = self.__imap_client.search('UNSEEN')
            for _, message_data in self.__imap_client.fetch(messages, "RFC822").items():
                message = email.message_from_bytes(message_data[b"RFC822"], policy=policy.default)
                sender = parseaddr(message.get("From"))[1]
                sourceEvent = SourceEvent()
                sourceEvent.source = SourceEvent.SOURCE_MAIL
                sourceEvent.timestamp = message.get('Date')
                sourceEvent.sender = sender
                sourceEvent.raw = message.get_body('plain').get_payload()  # type: ignore[attr-defined]
                if self.isSenderAllowed(allowlist=self.__allowlist, denylist=self.__denylist, sender=sender):
                    parsedSourceEvent = self.parser.parseMessage(sourceEvent, None)  # type: ignore[union-attr]
                    return parsedSourceEvent
                else:
                    self.error("Received unhandled message (ignored sender)")
                    return UnhandledEvent.fromSourceEvent(sourceEvent, UnhandledEvent.CAUSE_IGNORED_SENDER)
        except (timeout, OSError) as e:
            self.error("Connection to mailserver timed out")
            self.__connect()

    def getSourceState(self) -> SourceState:
        if self.__connected:
            return SourceState.OK
        return SourceState.ERROR

    def __connect(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Workaround for test
        context.set_ciphers('DEFAULT@SECLEVEL=1')  # Workaround for test
        server = self.getSettingString("mail_server", "")
        user = self.getSettingString("mail_user", "")
        password = self.getSettingString("mail_password", "")
        try:
            if self.isDebug():
                self.print("Connecting to server {}".format(server))
            self.__imap_client = IMAPClient(server, use_uid=True, ssl_context=context, timeout=1.0)
        except gaierror:
            self.error("Failed to connect to Mail Server")
        else:
            try:
                if self.isDebug():
                    self.print("Login as user {}".format(user))
                self.__imap_client.login(user, password)
            except LoginError:
                self.error("Mail Server login failed")
            else:
                if self.isDebug():
                    self.print("Login successful")
                self.__imap_client.select_folder('INBOX', readonly=False)
