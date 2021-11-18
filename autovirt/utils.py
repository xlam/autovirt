import os
import logging

from config import log_dir
from autovirt.logger import Logger


def get_log_dir():
    logging_dir = os.path.join(os.path.normpath(os.getcwd()), log_dir)
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir


def init_logger(name: str) -> logging.Logger:
    return Logger(name=name, log_dir=get_log_dir())  # type: ignore


def get_logger() -> logging.Logger:
    return Logger()  # type: ignore


def normalize(value: float, min_value: float, max_value: float):
    """Normalize value to the range 0..1"""
    if not min_value <= value <= max_value:
        raise ValueError(f"Value {value} is not in range [{min_value}; {max_value}]")
    return (value - min_value) / (max_value - min_value)
