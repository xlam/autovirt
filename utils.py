# %%
import json
import logging
import requests

import config


# %%
def get_logger(name: str):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.hasHandlers():
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'{name}.log')

        c_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s')
        c_handler.setFormatter(c_formatter)
        f_handler.setFormatter(c_formatter)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger


# %%
def get_logged_session():
    s = requests.Session()
    s.post('https://virtonomica.ru/vera/main/user/login', {
        'userData[login]': config.login,
        'userData[password]': config.password,
        'remember': 1,
    })
    return s


# %%
def get_token(s: requests.Session):
    r = s.get('https://virtonomica.ru/api/'
              '?app=system&action=token&format=json')
    return json.loads(r.content)
