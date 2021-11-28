import os
import pickle
import requests
import datetime
from typing import Optional, Any

import config
from autovirt.utils import get_logger

logger = get_logger()


class VirtSession(requests.Session):

    session: Any = None

    def __init__(self):
        requests.Session.__init__(self)

    def login(self):
        r = self.post(
            "https://virtonomica.ru/api/vera/user/login",
            {
                "email": config.login,
                "password": config.password,
            },
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Virtonomica login has failed (status code {r.status_code})"
            )

    @staticmethod
    def warn_status_not_ok(res: requests.Response):
        if res.status_code != 200:
            logger.warning(f"HTTP status code {res.status_code} for {res.url}")

    def get(self, *args, **kwargs):
        res = requests.Session.get(self, *args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def post(self, *args, **kwargs):
        res = requests.Session.post(self, *args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def save_session(self):
        with open(config.session_file, "wb") as f:
            pickle.dump(self, f)

    @property
    def token(self) -> str:
        r = self.get("https://virtonomica.ru/api/vera/main/token")
        return r.json()


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_cached_session() -> Optional[VirtSession]:
    if not os.path.exists(config.session_file):
        return None
    time = modification_date(config.session_file)
    last_mod_time = (datetime.datetime.now() - time).seconds
    if last_mod_time < config.session_timeout:
        with open(config.session_file, "rb") as f:
            s = pickle.load(f)
            logger.info("cached session loaded")
            return s
    return None


def get_logged_session() -> VirtSession:
    if not VirtSession.session:
        s = get_cached_session()
        if not s:
            s = VirtSession()
            s.login()
            logger.info("new session initialized")
        VirtSession.session = s
    return VirtSession.session
