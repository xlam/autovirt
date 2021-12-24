import os
import pickle
import requests
import datetime
from typing import Optional

from autovirt.utils import get_logger, get_config


class VirtSession:
    def __init__(self, session: Optional[requests.Session] = None):
        self.session: Optional[requests.Session] = session
        self.logger = get_logger()
        self.config = get_config("autovirt")

    def get_logged_session(self) -> requests.Session:
        if not self.session:
            s = self.get_cached_session()
            if not s:
                s = requests.Session()
                self.login()
                self.logger.info("new session initialized")
            self.session = s
        return self.session

    def login(self):
        r = self.session.post(
            "https://virtonomica.ru/api/vera/user/login",
            {
                "email": self.config["login"],
                "password": self.config["password"],
            },
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Virtonomica login has failed (status code {r.status_code})"
            )

    def warn_status_not_ok(self, res: requests.Response):
        if res.status_code != 200:
            self.logger.warning(f"HTTP status code {res.status_code} for {res.url}")

    def get(self, *args, **kwargs):
        s = self.get_logged_session()
        res = s.get(*args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def post(self, *args, **kwargs):
        s = self.get_logged_session()
        res = s.post(*args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def save_session(self):
        with open(self.config["session_file"], "wb") as f:
            pickle.dump(self.session, f)

    @property
    def token(self) -> str:
        s = self.get_logged_session()
        r = s.get("https://virtonomica.ru/api/vera/main/token")
        return r.json()

    @staticmethod
    def modification_date(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def get_cached_session(self) -> Optional[requests.Session]:
        if not os.path.exists(self.config["session_file"]):
            return None
        time = VirtSession.modification_date(self.config["session_file"])
        last_mod_time = (datetime.datetime.now() - time).total_seconds()
        if last_mod_time < self.config["session_timeout"]:
            with open(self.config["session_file"], "rb") as f:
                s = pickle.load(f)
                self.logger.info("cached session loaded")
                return s
        return None
