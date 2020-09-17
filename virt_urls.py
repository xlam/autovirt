from lxml import etree as et
from lxml import html
import requests
import pandas as pd
import json
import time

# set pandas float format
pd.options.display.float_format = '{:.2f}'.format
pd.options.display.max_rows = 101

login = ''
password = ''
company_id = -1

# make session
s = requests.Session()
s.post('https://virtonomica.ru/vera/main/user/login', {
    'userData[login]': login,
    'userData[password]': password,
    'remember': 1,
})

# get system messages
messages = s.get(
    'https://virtonomica.ru/api/vera/main/user/message/browse?tpl=user%2Fmessages%2Fmessages-system&box=system&sort=created%2Fdesc&pagesize=20&ajax=1&app=adapter_vrt&format=json&undefined=undefined&wrap=0')

print(messages.text)