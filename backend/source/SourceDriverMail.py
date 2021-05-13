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
        # Settings
        self.__server = self.getSettingString("server", "")
        self.__user = self.getSettingString("user", "")
        self.__password = self.getSettingString("password", "")
        self.__ssl = self.getSettingBoolean("ssl", True)
        self.__fix_weak_dh = self.getSettingBoolean("fix_weak_dh", False)
        self.__allowlist = self.getSettingList("allowlist", [])
        self.__denylist = self.getSettingList("denylist", [])
        self.__cleanup = self.getSettingString("cleanup", "")
        self.__archive_folder = self.getSettingString("archive_folder", "Archive")

        if self.__cleanup == "Delete":
            self.print("Cleanup strategy is delete")
        elif self.__cleanup == "Archive":
            self.print("Cleanup strategy is archive")
        elif self.__cleanup == "":
            self.print("Cleanup is disabled")
        else:
            self.fatal("Unknown cleanup strategy")

        # Internal
        self.__healthy = False

        self.__connect()

    def retrieveEvent(self) -> Optional[SourceEvent]:
        try:
            if self.isDebug():
                self.print("Checking for new mails")
            messages = self.__imap_client.search('UNSEEN')
            for uid, message_data in self.__imap_client.fetch(messages, "RFC822").items():
                message = email.message_from_bytes(message_data[b"RFC822"], policy=policy.default)
                sender = parseaddr(message.get("From"))[1]
                sourceEvent = SourceEvent()
                sourceEvent.source = SourceEvent.SOURCE_MAIL
                sourceEvent.timestamp = message.get('Date')
                sourceEvent.sender = sender
                sourceEvent.raw = message
                if self.isSenderAllowed(allowlist=self.__allowlist, denylist=self.__denylist, sender=sender):
                    #parsedSourceEvent = self.parser.parseMessage(sourceEvent, None)  # type: ignore[union-attr]
                    self.__do_cleanup(uid)
                    return parsedSourceEvent
                else:
                    self.error("Received unhandled message (ignored sender)")
                    return UnhandledEvent.fromSourceEvent(sourceEvent, UnhandledEvent.CAUSE_IGNORED_SENDER)
        except (timeout, OSError) as e:
            self.error("Connection to mailserver timed out")
            self.__healthy = False
            self.__connect()

    def getSourceState(self) -> SourceState:
        if self.__healthy:
            return SourceState.OK
        return SourceState.ERROR

    def __connect(self):
        if self.__fix_weak_dh:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Workaround for weak dh key
            context.set_ciphers('DEFAULT@SECLEVEL=1')
        else:
            context = ssl.SSLContext()

        try:
            if self.isDebug():
                self.print("Connecting to server {}".format(self.__server))
            self.__imap_client = IMAPClient(self.__server, use_uid=True,ssl=self.__ssl, ssl_context=context, timeout=1.0)
        except gaierror:
            self.error("Failed to connect to Mail Server")
        except ssl.SSLError:
            self.fatal("Failed to connect to Mail Server (TLS Error)")
        else:
            try:
                if self.isDebug():
                    self.print("Login as user {}".format(self.__user))
                self.__imap_client.login(self.__user, self.__password)
            except LoginError:
                self.error("Mail Server login failed")
            else:
                if self.isDebug():
                    self.print("Login successful")
                self.__healthy = True
                self.__imap_client.select_folder('INBOX', readonly=False)

    def __create_imap_folder(self, folder):
        if not self.__imap_client.folder_exists(folder):
            self.print("Folder {} does not exist creating")
            self.__imap_client.create_folder(folder)

    def __do_cleanup(self, uid):
        if self.__cleanup == "Archive":
            self.__create_imap_folder(self.__archive_folder)
            self.__imap_client.copy(uid, self.__archive_folder)
        if self.__cleanup == "Delete" or self.__cleanup == "Archive":
            self.__imap_client.delete_messages(uid)
            self.__imap_client.expunge(uid)
