import datetime
import os
import pickle
from typing import Optional

import requests
from pydantic import BaseModel

from autovirt.utils import get_config, get_logger


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
            f"{self.options.base_url}/main/user/login",
            data={
                "email": self.options.login,
                "password": self.options.password,
            },
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Virtonomica login has failed (status code {r.status_code})"
            )

        # Add critical cookies required for API endpoints after successful login
        # These cookies are typically set during full web login and are required
        # for certain API endpoints like /main/company/employee/recruiting
        # Values are loaded from config to avoid hardcoding private data
        config = get_config("autovirt")
        mm_key = config.get("_mm_key_")
        mm_user = config.get("_mm_user_")

        if mm_key:
            session.cookies.set("_mm_key_", mm_key, domain="virtonomica.ru")
        if mm_user:
            session.cookies.set("_mm_user_", mm_user, domain="virtonomica.ru")

    def get_token(self, session: requests.Session) -> str:
        """Get token for additional requests"""
        r = session.get(f"{self.options.base_url}/main/token")
        return r.json()

    def warn_status_not_ok(self, res: requests.Response):
        if res.status_code != 200:
            self.logger.warning(f"HTTP status code {res.status_code} for {res.url}")

    def get(self, *args, **kwargs) -> requests.Response:
        s = self.get_logged_session()
        # Add referer header for API calls to match expected browser behavior
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if "Referer" not in kwargs["headers"]:
            kwargs["headers"]["Referer"] = f"{self.options.base_url}/main"

        # Log request details for debugging
        self.logger.info(
            f"GET request to: {args[0] if args else kwargs.get('url', 'unknown')}"
        )
        self.logger.info(f"Headers: {kwargs['headers']}")
        self.logger.info(f"Params: {kwargs.get('params', {})}")
        self.logger.info(f"Cookies: {dict(s.cookies)}")

        res = s.get(*args, **kwargs)

        self.logger.info(f"Response status: {res.status_code}")
        self.logger.info(f"Response headers: {dict(res.headers)}")

        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def post(self, *args, **kwargs) -> requests.Response:
        s = self.get_logged_session()
        # # Add referer header for API calls to match expected browser behavior
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if "Referer" not in kwargs["headers"]:
            kwargs["headers"]["Referer"] = f"{self.options.base_url}/main"

        # Log request details for debugging
        self.logger.info(
            f"POST request to: {args[0] if args else kwargs.get('url', 'unknown')}"
        )
        self.logger.info(f"Headers: {kwargs['headers']}")
        self.logger.info(f"Data/Params: {kwargs.get('data', kwargs.get('params', {}))}")
        self.logger.info(f"Cookies: {dict(s.cookies)}")

        res = s.post(*args, **kwargs)

        self.logger.info(f"Response status: {res.status_code}")
        self.logger.info(f"Response headers: {dict(res.headers)}")

        self.warn_status_not_ok(res)
        self.save_session()
        return res

    def save_session(self):
        with open(self.options.session_file, "wb") as f:
            pickle.dump(self.session, f)

    @property
    def token(self) -> str:
        s = self.get_logged_session()
        # Use the get method which includes proper headers
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
