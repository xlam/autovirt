#!/usr/bin/env python
# coding: utf-8

import json

import config
from autovirt import utils

logger = utils.get_logger("salary")
logger.info("starting salary update")

s = utils.get_logged_session()
token = utils.get_token(s)
pagesize = 1000


def get_units_to_update_salary() -> list[dict]:
    r = s.get(
        f"https://virtonomica.ru/api/vera/main/company/employee/units?"
        f"id={config.company_id}"
        f"&pagesize={pagesize}"
    )
    data = json.loads(r.content)
    units = []
    for _, unit in data["data"].items():
        if float(unit["labor_level"]) < float(unit["employee_level_required"]):
            units.append(unit)
    return units


def run(config_name):
    if not config_name:
        pass

    units = get_units_to_update_salary()

    if not units:
        logger.info("no units to update salary, exiting.")
        quit(0)
    logger.info(f"{len(units)} units to update salary")

    for unit in units:
        r = s.get(
            f"https://virtonomica.ru/api/vera/main/unit/employee/info"
            f"?id={unit['id']}"
        )
        data = json.loads(r.content)
        # set salary to required plus 5$ for sure
        salary = round(data["salary_required"]) + 5
        logger.info(
            f"updating salary at unit "
            f"{unit['id']} ({unit['name']}, {unit['city_name']}) from "
            f"{unit['labor_salary']} to {salary}"
        )
        s.post(
            f"https://virtonomica.ru/api/vera/main/unit/employee/update",
            {
                "id": unit["id"],
                "employee_count": unit["labor_qty"],
                "employee_salary": salary,
                "token": token,
            },
        )
