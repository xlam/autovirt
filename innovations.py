#!/usr/bin/env python
# coding: utf-8

# %%
import time
import json

import utils


# %%
logger = utils.get_logger('innovations')
s = utils.get_logged_session()
token = utils.get_token(s)


# %%
# this uses virtonomica's API and should work for any site design
def attach_artefact(name, unit_id):

    # get unit artefact slots
    r = s.get(f'https://virtonomica.ru/api/vera/main/unit/artefact/slots'
              f'?id={unit_id}&format=json')
    slots = json.loads(r.content)

    # get all artefacts for unit
    artefacts = dict()
    for (sid, _) in slots.items():
        r = s.get(f'https://virtonomica.ru/api/vera/main/unit/artefact/browse'
                  f'?id={unit_id}&slot_id={sid}&format=json')
        artefacts.update(json.loads(r.content))

    url = 'https://virtonomica.ru/api/vera/main/unit/artefact/attach'

    for (aid, artefact) in artefacts.items():
        if artefact['name'] == name:
            params = {
                'id': unit_id,
                'artefact_id': artefact['id'],
                'token': token,
            }
            logger.info(f'renewing: ({unit_id}) {name}')
            r = s.post(url, params)
            logger.info(r)
            break


def get_system_messages():
    r = s.get('https://virtonomica.ru/api/vera/main/user/message/browse'
              '?tpl=user%2Fmessages%2Fmessages-system'
              '&box=system'
              '&sort=created%2Fdesc'
              '&pagesize=20'
              '&ajax=1'
              '&app=adapter_vrt'
              '&format=json'
              '&undefined=undefined'
              '&wrap=0')

    return json.loads(r.content)


def build_innovations_renewal_list(messages):
    subj_string = 'Время жизни инноваций на предприятиях подошло к концу!'
    renewal = []
    for (_, message) in messages['data'].items():
        if message['subject'] == subj_string:
            for (_, attach) in message['attaches'].items():
                renewal.append((attach['object_id'], attach['tag']))
    return renewal


def delete_innovations_renewal_messages(messages):
    # token = get_token()
    subj_string = 'Время жизни инноваций на предприятиях подошло к концу!'
    for (mid, message) in messages['data'].items():
        if message['subject'] == subj_string:
            url = f'https://virtonomica.ru/api/' \
                  f'?action=user/message/del&app=virtonomica&' \
                  f'message_id={mid}&box=system&token={token}'
            logger.info(f'deleting message: {mid}')
            time.sleep(3)
            s.get(url)


def renew_innovations():
    messages = get_system_messages()
    renewal = build_innovations_renewal_list(messages)
    if not renewal:
        logger.info('nothing to renew, exiting')
        exit(0)
    for item in renewal:
        time.sleep(3)
        attach_artefact(item[1], item[0])
    delete_innovations_renewal_messages(messages)


# %%
logger.info('starting innovations renewal')
renew_innovations()
logger.info('finished innovations renewal')

# %%
# delete multiple messages:
# url: https://virtonomica.ru/api/?action=user/message/del&app=virtonomica
# params: message_id%5B%5D=73329072&message_id%5B%5D=73223981&box=inbox&token=5f454448d8178&method=POST&base_url=%2Fapi%2F
#
# delete single message:
# url: https://virtonomica.ru/api/?action=user/message/del&app=virtonomica
# params: message_id=73178018&box=inbox&token=5f454448d8178&method=POST&base_url=%2Fapi%2F
#
# get token (connection token?)
# https://virtonomica.ru/api/?app=system&action=token&format=json
#
# https://virtonomica.ru/api/?action=user/message/del&app=virtonomica&message_id=73192810&box=inbox&token=5f454c6b16b35
#
# "&box=inbox" for personal messages
# "&box=system" for system messages (innovations expiration etc.)

##
