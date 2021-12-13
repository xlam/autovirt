import os
import pickle
import requests
import datetime
from typing import Optional

from autovirt.utils import get_logger, get_config

logger = get_logger()
_config = get_config("autovirt")


class VirtSession(requests.Session):
    def __init__(self):
        requests.Session.__init__(self)

    def login(self):
        r = self.post(
            "https://virtonomica.ru/api/vera/user/login",
            {
                "email": _config["login"],
                "password": _config["password"],
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
        with open(_config["session_file"], "wb") as f:
            pickle.dump(self, f)

    @property
    def token(self) -> str:
        r = self.get("https://virtonomica.ru/api/vera/main/token")
        return r.json()


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_cached_session() -> Optional[VirtSession]:
    if not os.path.exists(_config["session_file"]):
        return None
    time = modification_date(_config["session_file"])
    last_mod_time = (datetime.datetime.now() - time).seconds
    if last_mod_time < _config["session_timeout"]:
        with open(_config["session_file"], "rb") as f:
            s = pickle.load(f)
            logger.info("cached session loaded")
            return s
    return None


_session: Optional[VirtSession] = None


def get_logged_session() -> VirtSession:
    global _session
    if not _session:
        s = get_cached_session()
        if not s:
            s = VirtSession()
            s.login()
            logger.info("new session initialized")
        _session = s
    return _session
