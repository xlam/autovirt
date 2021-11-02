import os
import logging

from config import log_dir
from autovirt.logger import Logger


def get_log_dir():
    logging_dir = os.path.join(os.path.normpath(os.getcwd()), log_dir)
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir


def init_logger(name: str) -> logging.Logger:
    return Logger(name=name, log_dir=get_log_dir())


def get_logger() -> logging.Logger:
    return Logger()
