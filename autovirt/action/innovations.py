#!/usr/bin/env python
# coding: utf-8

import time
import json

from autovirt import utils


logger = utils.get_logger("innovations")
s = utils.get_logged_session()
token = utils.get_token(s)


# this uses virtonomica's API and should work for any site design
def attach_artefact(name, unit_id):

    # get unit artefact slots
    r = s.get(f"https://virtonomica.ru/api/vera/main/unit/artefact/slots?id={unit_id}")
    slots = json.loads(r.content)

    # get all artefacts for unit
    artefacts = dict()
    for sid, _ in slots.items():
        r = s.get(
            f"https://virtonomica.ru/api/vera/main/unit/artefact/browse"
            f"?id={unit_id}&slot_id={sid}"
        )
        artefacts.update(json.loads(r.content))

    url = "https://virtonomica.ru/api/vera/main/unit/artefact/attach"

    for aid, artefact in artefacts.items():
        if artefact["name"] == name:
            params = {
                "id": unit_id,
                "artefact_id": artefact["id"],
                "token": token,
            }
            logger.info(f"renewing: ({unit_id}) {name}")
            r = s.post(url, params)
            logger.info(r)
            break


def get_system_messages() -> dict:
    r = s.get("https://virtonomica.ru/api/vera/main/user/message/browse?box=system")
    return json.loads(r.content)


def build_innovations_renewal_list(messages):
    # todo: do we need this ckeck?
    if not messages["data"]:
        return False
    subj_string = "Время жизни инноваций на предприятиях подошло к концу!"
    renewal = []
    for _, message in messages["data"].items():
        if message["subject"] == subj_string:
            for _, attach in message["attaches"].items():
                renewal.append((attach["object_id"], attach["tag"]))
    return renewal


def delete_innovations_renewal_messages(messages):
    # token = get_token()
    subj_string = "Время жизни инноваций на предприятиях подошло к концу!"
    for mid, message in messages["data"].items():
        if message["subject"] == subj_string:
            url = (
                f"https://virtonomica.ru/api/vera/main/user/message/del"
                f"?message_id={mid}"
                f"&box=system"
                f"&token={token}"
            )
            logger.info(f"deleting message: {mid}")
            time.sleep(3)
            s.get(url)


def renew_innovations():
    messages = get_system_messages()
    renewal = build_innovations_renewal_list(messages)
    if not renewal:
        logger.info("nothing to renew, exiting")
        exit(0)
    for item in renewal:
        time.sleep(3)
        attach_artefact(item[1], item[0])
    delete_innovations_renewal_messages(messages)


def run(config_name):
    if not config_name:
        pass

    logger.info("starting innovations renewal")
    renew_innovations()
    logger.info("finished innovations renewal")
