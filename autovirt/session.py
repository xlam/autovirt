import os
import pickle
import requests
import datetime
from pydantic import BaseModel
from typing import Optional

from autovirt.utils import get_logger, get_config


class VirtSessionOptions(BaseModel):
    session_file: str
    session_timeout: int
    base_url: str
    login: str
    password: str


class VirtSession:
    def __init__(
        self,
        session: Optional[requests.Session] = None,
        options: Optional[VirtSessionOptions] = None,
    ):
        self.session: Optional[requests.Session] = session
        self.logger = get_logger()
        self.options = (
            VirtSessionOptions(**get_config("autovirt")) if not options else options
        )

    def get_logged_session(self) -> requests.Session:
        if not self.session:
            s = self.get_cached_session()
            if not s:
                s = requests.Session()
                self.login(s)
                self.logger.info("new session initialized")
            self.session = s
            self.save_session()
        return self.session

    def login(self, session: requests.Session):
        r = session.post(
            f"{self.options.base_url}/user/login",
            {
                "email": self.options.login,
                "password": self.options.password,
            },
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Virtonomica login has failed (status code {r.status_code})"
            )

    def warn_status_not_ok(self, res: requests.Response):
        if res.status_code != 200:
            self.logger.warning(f"HTTP status code {res.status_code} for {res.url}")

    def get(self, *args, **kwargs) -> requests.Response:
        s = self.get_logged_session()
        res = s.get(*args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def post(self, *args, **kwargs) -> requests.Response:
        s = self.get_logged_session()
        res = s.post(*args, **kwargs)
        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def save_session(self):
        with open(self.options.session_file, "wb") as f:
            pickle.dump(self.session, f)

    @property
    def token(self) -> str:
        s = self.get_logged_session()
        r = s.get(f"{self.options.base_url}/main/token")
        return r.json()

    @staticmethod
    def modification_date(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def get_cached_session(self) -> Optional[requests.Session]:
        if not os.path.exists(self.options.session_file):
            return None
        time = VirtSession.modification_date(self.options.session_file)
        last_mod_time = (datetime.datetime.now() - time).total_seconds()
        if last_mod_time < self.options.session_timeout:
            with open(self.options.session_file, "rb") as f:
                s = pickle.load(f)
                self.logger.info("cached session loaded")
                return s
        return None
