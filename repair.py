#!/usr/bin/env python
# coding: utf-8

# %%
from lxml import etree as et
from lxml import html
import pandas as pd
import time

import config
import utils

# %%
logger = utils.get_logger('repair')
logger.info('starting repair')

# set pandas float format
pd.options.display.float_format = '{:.2f}'.format
pd.options.display.max_rows = 101


# %%
s = utils.get_logged_session()

# %%
# set units display count to maximum (400 units)
s.get('https://virtonomica.ru/vera/main/common/util/setpaging/dbunit/unitListWithEquipment/400')

# %%
# set equipment suppliers display count to maximum (400 units)
s.get('https://virtonomica.ru/vera/window/common/util/setpaging/dbunitsman/equipmentSupplierListByProductAndCompany/400')

# %%
# set filter to machine tools (id=1529)
s.post('https://virtonomica.ru/vera/main/common/util/setfiltering/dbunit/unitListWithEquipment/product=1529')

# %%
# get units list
units_list = s.get(f'https://virtonomica.ru/vera/main/company/view/{config.company_id}/unit_list/equipment')

# %%
# parse page
root = html.fromstring(units_list.content)

# %%
# get units table
table = root.xpath('//table[@class="list"]')[0]

# %%
# get all units checkboxes to extract ids
rows = table.xpath('//input[@onclick="selectUnit(this)"]')

# %%
et.tostring(rows[0], pretty_print=True)

# %%
# construct dictionary containing required units data
units = dict()
for row in rows:
    # unit id
    uid = row.get('id').split('_')[1]
    # equipment quantity
    qnt = table.xpath(f'//input[@id="qnt_{uid}"]/@value')[0]
    # max equipment quantity
    qnt_max = table.xpath(f'//input[@id="qnt_max_{uid}"]/@value')[0]
    # wear
    wear = table.xpath(f'//input[@id="wear_{uid}"]/@value')[0]
    # required equipment quality
    req = table.xpath(f'//input[@id="wear_{uid}"]/../preceding-sibling::td[1]/text()')[0]

    # virtonomica's API won't return proper suppliers if units wear is 0
    if float(wear) > 0:
        if req not in units.keys():
            units[req] = []
        units[req].append((uid, qnt, qnt_max, wear))

if not units:
    logger.info('nothing to repair, exiting')
    exit(0)

logger.info(f'Prepared units dict with {len(units)} quality levels:')
logger.info(units.keys())


# %%
def build_repair_params(units):
    res = dict()
    for (quality, units_list) in units.items():
        params = dict()
        for unit in units_list:
            params[f'units[{unit[0]}]'] = 1529 # 1529 = machine tools id
        params['company_id'] = config.company_id
        res[quality] = params
    return res


# %%
# load equipment suppliers page for units listed in params
def get_suppliers_page(session, params):
    response = session.post('https://virtonomica.ru/vera/window/management_units/equipment/repair', params)
    root = html.fromstring(response.content)
    return root


# %%
def get_quantity_to_repair(root):
    return int(root.xpath('//input[@name="quantity[from]"]/@value')[0])


# %%
# create pandas dataframe containing suppliers data
def get_suppliers_df(root):

    # get units table
    table = root.xpath('//table[@class="list"]')[0]

    # get all units radio button cells (<td>) to extract data
    rows = table.xpath('//input[@id="supplyData[offer]"]/..')

    # build list of suppliers
    suppliers = []
    for row in rows:
        # unit id
        uid = row.xpath('./input[@id="supplyData[offer]"]/@value')[0]
        # price
        price = row.xpath('./input[contains(@id, "totalOfferPrice")]/@value')[0]
        # quality
        qlt = row.xpath('./input[contains(@id, "quality")]/@value')[0]
        # quantity
        qnt = row.xpath('./input[contains(@id, "quantity")]/@value')[0]

        suppliers.append((uid, price, qlt, qnt))

    # create pandas dataframe
    df = pd.DataFrame(suppliers, columns=['id', 'price', 'quality', 'quantity'])
    df = df.apply(pd.to_numeric)
    df.sort_values(['quality'], ascending=False, inplace=True)
    logger.info(df.values)
    return df


# %%
# find best supplier. this part is a bit tricky and needs better selection algorithm
def get_supplier(df, quality, quantity):
    quality = float(quality)
    quantity = int(quantity)
    # select units in range [quality-2 ... quality+3] and having enough repair parts
    sup = df[(df['quality'] > quality-2) & (df['quality'] < quality+3) & (df['quantity'] > quantity)].copy()
    # calculate price/quality ratio
    sup['p/q'] = sup['price'] / sup['quality']
    logger.info(sup)
    # select one with lowest p/r ratio (mostly cheaper one)
    val = sup[sup['p/q'] == sup.min()['p/q']]
    return val.values


# %%
def repair(session, supplier_id):
    response = session.post('https://virtonomica.ru/vera/window/management_units/equipment/repair', {
        'supplyData[offer]': supplier_id,
        'submitRepair': 'Отремонтировать оборудование',
    })
    print(response)


# %%
def repair_by_quality(quality, params, fake=False):
    logger.info(f'Repairing items of quality {quality} (from {len(params)-1} units)...')
    
    suppliers_page = get_suppliers_page(s, params) # lxml page
    logger.info(f'got suppliers page...')

    suppliers = get_suppliers_df(suppliers_page) # pandas dataframe
    logger.info(f'created pandas dataframe...')
    logger.info(suppliers)

    quantity_to_repair = get_quantity_to_repair(suppliers_page)
    logger.info(f'{quantity_to_repair} pieces to repair...')

    supplier = get_supplier(suppliers, quality, quantity_to_repair)
    (sup_id, sup_price, sup_quality, sup_quantity) = supplier.values[0]
    logger.info(f'got supplier {sup_id} for quality of {quality} (quality={sup_quality}, price={sup_price})...')

    logger.info(f'waiting for 3 seconds...')
    time.sleep(3)

    if fake:
        logger.info(f'fake repairing...')
    else:
        logger.info(f'repairing...')
        repair(s, sup_id) # s = session


# %%
def repair_all(rep_params):
    for (quality, params) in rep_params.items():
        repair_by_quality(quality, params)


# %%
# qual = '36.22'
# repair_one(qual, rep_params[qual])
repair_all(build_repair_params(units))
