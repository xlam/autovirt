#!/usr/bin/env python
# coding: utf-8

import time
import json

from autovirt import utils


logger = utils.get_logger("employee")
s = utils.get_logged_session()
token = utils.get_token(s)


def get_system_messages():
    r = s.get(
        "https://virtonomica.ru/api/vera/main/user/message/browse"
        "?tpl=user%2Fmessages%2Fmessages-system&box=system&format=json"
    )
    return json.loads(r.content)


def build_salary_rise_list(messages):
    if not messages["data"]:
        return False
    subj_string = "Недовольство заработной платой"
    units = []
    for (_, message) in messages["data"].items():
        if message["subject"] == subj_string:
            for (_, attach) in message["attaches"].items():
                units.append(
                    {
                        "id": attach["object_id"],
                        "name": attach["object_name"],
                        "salary_demanded": float(attach["tag"]),
                    }
                )
    return units


def delete_salary_rise_messages(messages):
    subj_string = "Недовольство заработной платой"
    for (mid, message) in messages["data"].items():
        if message["subject"] == subj_string:
            url = (
                f"https://virtonomica.ru/api/"
                f"?action=user/message/del&app=virtonomica&"
                f"message_id={mid}&box=system&token={token}"
            )
            logger.info(f"deleting message: {mid}")
            time.sleep(3)
            s.get(url)


def rise_salary():

    messages = get_system_messages()
    units = build_salary_rise_list(messages)

    if not units:
        logger.info("no units to rise salary, exiting.")
        return

    for unit in units:
        r = s.get(
            f"https://virtonomica.ru/api/vera/main/unit/employee/info?"
            f"id={unit['id']}"
        )
        data = json.loads(r.content)
        salary = round(unit["salary_demanded"]) + 5
        logger.info(
            f"raising salary at {unit['name']} ({unit['id']}) "
            f"from {data['employee_salary']} to {salary}"
        )
        s.post(
            f"https://virtonomica.ru/api/vera/main/unit/employee/update",
            {
                "id": unit["id"],
                "employee_count": data["employee_count"],
                "employee_salary": salary,
                "token": token,
            },
        )

    delete_salary_rise_messages(messages)


def run(config_name):
    if not config_name:
        pass

    logger.info("starting salary rising")
    rise_salary()
    logger.info("finished salary rising")
