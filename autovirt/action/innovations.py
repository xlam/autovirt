import sys
import time
from typing import Optional

from autovirt import utils
from autovirt.action.interface import MailInterface, ArtefactInterface
from autovirt.structs import Message

logger = utils.get_logger()


def build_innovations_renewal_list(messages: list[Message]):
    renewal = []
    for message in messages:
        for attach in message.attaches:
            renewal.append(attach)
    return renewal


class InnovationsAction:
    subject: str = "Время жизни инноваций на предприятиях подошло к концу!"

    def __init__(
        self, mail_gateway: MailInterface, artefact_gateway: ArtefactInterface
    ):
        self.mail = mail_gateway
        self.artefact = artefact_gateway

    def renew_innovations(self):
        messages = self.mail.get_messages(self.subject)
        if not messages:
            logger.info("nothing to renew, exiting")
            sys.exit(0)
        renewal = build_innovations_renewal_list(messages)
        for item in renewal:
            time.sleep(1)
            self.artefact.attach(item["tag"], item["object_id"])
        self.mail.delete_messages(messages)

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass
        self.renew_innovations()
