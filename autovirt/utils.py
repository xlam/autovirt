import os
import logging
from typing import Any, Sequence
from functools import reduce

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
    if min_value == max_value:
        return 0
    if not min_value <= value <= max_value:
        raise ValueError(f"Value {value} is not in range [{min_value}; {max_value}]")
    return (value - min_value) / (max_value - min_value)


def get_max(objects: Sequence[object], field: str) -> Any:
    """Get maximum value of a field in the sequence of objects"""
    return reduce(
        lambda x, y: max([x, getattr(y, field)]), objects, getattr(objects[0], field)
    )


def get_min(objects: Sequence[object], field: str) -> Any:
    """Get minimum value of a field in the sequence of objects"""
    return reduce(
        lambda x, y: min([x, getattr(y, field)]), objects, getattr(objects[0], field)
    )
