#!/usr/bin/env python
# coding: utf-8

# In[30]:


import re
#from IPython.core.display import display, HTML, Pretty
#from bs4 import BeautifulSoup
from lxml import etree as et
from lxml import html
import lxml
import requests
import pandas as pd
import time


# In[24]:


# set pandas float format
pd.options.display.float_format = '{:.2f}'.format
pd.options.display.max_rows = 101


# In[3]:


login = ''
password = ''
company_id = -1


# In[4]:


s = requests.Session()
s.post('https://virtonomica.ru/vera/main/user/login', {
     'userData[login]': login,
     'userData[password]': password,
     'remember': 1,
})


# In[5]:


# set units display count to maximum (400 units)
s.get('https://virtonomica.ru/vera/main/common/util/setpaging/dbunit/unitListWithEquipment/400')


# In[6]:


# set equipment suppliers display count to maximum (400 units)
s.get('https://virtonomica.ru/vera/window/common/util/setpaging/dbunitsman/equipmentSupplierListByProductAndCompany/400')


# In[7]:


# set filter to machine tools (id=1529)
s.post('https://virtonomica.ru/vera/main/common/util/setfiltering/dbunit/unitListWithEquipment/country=/region=/city=/product=1529/understaffed=/wear_percent=/low_quality=/animal_food_not_enough=/animal_food_low_quality=/type=0')


# In[8]:


# get units list
units_list = s.get(f'https://virtonomica.ru/vera/main/company/view/{company_id}/unit_list/equipment')


# In[9]:


# parse page
root = html.fromstring(units_list.content)


# In[10]:


# get units table
table = root.xpath('//table[@class="list"]')[0]


# In[11]:


# get all units checkboxes to extract ids
rows = table.xpath('//input[@onclick="selectUnit(this)"]')


# In[12]:


et.tostring(rows[0], pretty_print=True)


# In[13]:


# construct dictionary containing required units data 

units = dict()
for row in rows:
    # unit id
    uid = row.get('id').split('_')[1]
    # equipment quantity
    qnt = table.xpath(f'//input[@id="qnt_{uid}"]/@value')[0]
    # max quipment quantity
    qnt_max = table.xpath(f'//input[@id="qnt_max_{uid}"]/@value')[0]
    # wear
    wear = table.xpath(f'//input[@id="wear_{uid}"]/@value')[0]
    # required equipment quality
    req = table.xpath(f'//input[@id="wear_{uid}"]/../preceding-sibling::td[1]/text()')[0]
    
    if req not in units.keys():
        units[req] = []

    units[req].append((uid, qnt, qnt_max, wear))
    
    #print(cid, qnt, qnt_max, wear, req)

print(f'Prepeared units dict with {len(units)} quality levels:')
print(units.keys())


# In[14]:


def build_repair_params(units):
    res = dict()
    for (quality, units_list) in units.items():
        params = dict()
        for unit in units_list:
            params[f'units[{unit[0]}]'] = 1529 # 1529 = machine tools id
        params['company_id'] = company_id
        res[quality] = params
    return res


# In[15]:


# load equipment suppliers page for units listed in params
def get_suppliers_page(session, params):
    response = session.post('https://virtonomica.ru/vera/window/management_units/equipment/repair', params)
    root = html.fromstring(response.content)
    return root


# In[16]:


def get_quantity_to_repair(root):
    return int(root.xpath('//input[@name="quantity[from]"]/@value')[0])


# In[17]:


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
    
    return df


# In[18]:


# find best supplier. this part is a bit tricky and needs better selection algorithm
def get_supplier_id(df, quality, quantity):
    quality = float(quality)
    quantity = int(quantity)
    # select units in range [quality-2 ... quality+3] and having enough repair parts
    sup = df[(df['quality'] > quality-2) & (df['quality'] < quality+3) & (df['quantity'] > quantity)].copy()
    # calculate price/quality ratio
    sup['p/q'] = sup['price'] / sup['quality']
    # select one with lowest p/r ratio (mostly cheaper one)
    val = sup['id'][sup['p/q'] == sup.min()['p/q']]
    return val.values[0]


# In[32]:


def repair(session, supplier_id):
    response = session.post('https://virtonomica.ru/vera/window/management_units/equipment/repair', {
        'supplyData[offer]': supplier_id,
        'submitRepair': 'Отремонтировать оборудование',
    })
    print(response)


# In[31]:


def repair_one(quality, params):
    print(f'Repairing items of quality {quality} (from {len(params)-1} units)...')
    
    print(f'getting suppliers page...')
    suppliers_page = get_suppliers_page(s, params) # lxml page
    print(f'\t: {suppliers_page}')
    
    print(f'creating pandas dataframe...')
    suppliers = get_suppliers_df(suppliers_page) # pandas dataframe
    #print(f'{suppliers}')
    
    print(f'getting quantity to repair...')
    quantity_to_repair = get_quantity_to_repair(suppliers_page)
    print(f'\t{quantity_to_repair}')
    
    print(f'getting supplier id for quality of {quality}...')
    supplier_id = get_supplier_id(suppliers, quality, quantity_to_repair)
    print(f'\t{supplier_id}')
 
    print(f'waiting for 3 seconds...')
    time.sleep(3)

    print(f'repairing...')
    repair(s, supplier_id) # s = session


# In[33]:


def repair_all(rep_params):
    for (quality, params) in rep_params.items():
        repair_one(quality, params)
        print(f'waiting for 3 seconds...')
        time.sleep(3)


# In[34]:


#qual = '36.22'
#repair_one(qual, rep_params[qual])
repair_all(build_repair_params(units))


# In[ ]:





# In[ ]:





# In[ ]:




