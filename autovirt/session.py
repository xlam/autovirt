import os
import pickle
import requests
import datetime
from typing import Union

import config
from autovirt.utils import get_logger


class VirtSession(requests.Session):
    def __init__(self):
        self.logger = get_logger("utils_session")
        requests.Session.__init__(self)

    def get(self, *args, **kwargs):
        res = requests.Session.get(self, *args, **kwargs)
        self.save_session()
        return res

    def post(self, *args, **kwargs):
        res = requests.Session.post(self, *args, **kwargs)
        self.save_session()
        return res

    def save_session(self):
        with open(config.session_file, "wb") as f:
            pickle.dump(self, f)


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_cached_session() -> Union[VirtSession, None]:
    logger = get_logger("utils_session")
    if not os.path.exists(config.session_file):
        return None
    time = modification_date(config.session_file)
    last_mod_time = (datetime.datetime.now() - time).seconds
    if last_mod_time < config.session_timeout:
        with open(config.session_file, "rb") as f:
            s = pickle.load(f)
            logger.info(f"Cached session loaded")
            return s


def get_logged_session() -> VirtSession:
    logger = get_logger("utils_session")
    s = get_cached_session()
    if not s:
        s = VirtSession()
        s.post(
            "https://virtonomica.ru/vera/main/user/login",
            {
                "userData[login]": config.login,
                "userData[password]": config.password,
                "remember": 1,
            },
        )
        logger.info("New session initialized")
    return s


def get_token(s: requests.Session):
    r = s.get("https://virtonomica.ru/api/vera/main/token")
    return r.json()


session = get_logged_session()
token = get_token(session)
