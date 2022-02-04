import sys
import time
from typing import Optional

from autovirt import utils
from autovirt.mail.interface import MailGateway
from autovirt.artefact.interface import ArtefactGateway
from autovirt.artefact.domain import build_innovations_renewal_list

logger = utils.get_logger()


class RenewAction:
    subject: str = "Время жизни инноваций на предприятиях подошло к концу!"

    def __init__(self, mail_gateway: MailGateway, artefact_gateway: ArtefactGateway):
        self.mail = mail_gateway
        self.artefact = artefact_gateway

    def renew_innovations(self):
        messages = self.mail.get_messages_by_subject(self.subject)
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
