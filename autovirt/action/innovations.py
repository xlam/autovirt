import sys
import time

from autovirt import utils
from autovirt.virtapi import mail
from autovirt.virtapi import artefact
from autovirt.structs import Message


logger = utils.get_logger("innovations")


def build_innovations_renewal_list(messages: list[Message]):
    renewal = []
    for message in messages:
        for attach in message.attaches:
            renewal.append(attach)
    return renewal


def renew_innovations():
    messages = mail.get_messages(
        subject="Время жизни инноваций на предприятиях подошло к концу!"
    )
    if not messages:
        logger.info("nothing to renew, exiting")
        sys.exit(0)
    renewal = build_innovations_renewal_list(messages)
    for item in renewal:
        time.sleep(1)
        artefact.attach(item["tag"], item["object_id"])
    mail.delete_messages(messages)


def run(config_name):
    if not config_name:
        pass

    logger.info("starting innovations renewal")
    renew_innovations()
    logger.info("finished innovations renewal")
