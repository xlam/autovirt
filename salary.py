#!/usr/bin/env python
# coding: utf-8

# %%

import json

from lxml import html

import config
import utils

# %%
logger = utils.get_logger('salary')
logger.info('starting salary update')

# %%
s = utils.get_logged_session()

# %%
token = utils.get_token(s)

# %%
# set units display count to maximum (400 units)
s.get(
    'https://virtonomica.ru/vera/main/common/util/setpaging/dbunit'
    '/unitListWithHoliday/400')

# %%
# get units list page
r = s.get(
    f'https://virtonomica.ru/vera/main/company/view/'
    f'{config.company_id}/unit_list/employee')

# %%
# parse page
units_page = html.fromstring(r.content)


# %%
def get_units_to_update_salary(page: html.HtmlElement):
    # get all units td with actual and required employee level
    rows = page.xpath('//input[starts-with(@id, "employee_level_required")]/..')
    units = []
    for row in rows:
        uid = row.xpath('./input/@id')[0].split('_')[-1]
        level_actual = row.xpath('./a/text()')[0]
        level_required = row.xpath('./input/@value')[0]
        # print(f'uid: {uid}, act: {level_actual}, req: {level_required}')
        if float(level_actual) < float(level_required):
            # print(f'add {uid}')
            units.append((uid, level_actual, level_required))
    return units


# %%
units = get_units_to_update_salary(units_page)
if not units:
    logger.info('no units to update salary, exiting.')
    quit(0)
logger.info(f'{len(units)} units to update salary')

# %%
for unit in units:
    r = s.get(f'https://virtonomica.ru/api/vera/main/unit/employee/info?'
              f'id={unit[0]}')
    data = json.loads(r.content)
    # set salary to required plus 5$ for sure
    salary = round(data['salary_required']) + 5
    logger.info(f"updating salary at unit {unit[0]} from "
                f"{data['employee_salary']} to {salary}")
    s.post(f'https://virtonomica.ru/api/vera/main/unit/employee/update',
           {
               'id': unit[0],
               'employee_count': data['employee_count'],
               'employee_salary': salary,
               "token": token,
           })

# %%
