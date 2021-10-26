import os
import json
import pickle
import logging
import requests
import datetime

import config


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


def get_log_dir():
    log_dir = os.path.join(os.path.normpath(os.getcwd()), config.log_dir)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_logger(name: str):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.hasHandlers():
        filename = f"{name}.log"
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(os.path.join(get_log_dir(), filename))

        c_formatter = logging.Formatter(
            "%(asctime)s %(levelname)s (%(name)s): %(message)s"
        )
        c_handler.setFormatter(c_formatter)
        f_handler.setFormatter(c_formatter)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger


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


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_cached_session() -> VirtSession:
    logger = get_logger("utils_session")
    if not os.path.exists(config.session_file):
        return False
    time = modification_date(config.session_file)
    last_mod_time = (datetime.datetime.now() - time).seconds
    if last_mod_time < config.session_timeout:
        with open(config.session_file, "rb") as f:
            s = pickle.load(f)
            logger.info(f"Cached session loaded")
            return s


def get_token(s: requests.Session):
    r = s.get("https://virtonomica.ru/api/?app=system&action=token&format=json")
    return json.loads(r.content)
