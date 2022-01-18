import logging
import os
from typing import Any, Sequence

from autovirt.logger import Logger
from autovirt.config import config


def get_config(section: str) -> dict:
    return config()[section]


def get_log_dir():
    _config = get_config("autovirt")
    logging_dir = os.path.join(os.path.normpath(os.getcwd()), _config["log_dir"])
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir


def init_logger(name: str) -> logging.Logger:
    return Logger(name=name, log_dir=get_log_dir())  # type: ignore


def get_logger() -> logging.Logger:
    return Logger()  # type: ignore


def normalize(value: float, min_value: float, max_value: float) -> float:
    """Normalize value to range [0..1]"""
    if min_value == max_value:
        return 0
    if not min_value <= value <= max_value:
        raise ValueError(f"Value {value} is not in range [{min_value}; {max_value}]")
    return (value - min_value) / (max_value - min_value)


def normalize_array(array: Sequence[float]) -> Sequence[float]:
    """Normalize array to range [0..1]"""
    if not array:
        raise ValueError(f"array is empty")
    min_value = min(array)
    max_value = max(array)
    if min_value == max_value:
        return [0 for _ in array]
    return [normalize(value, min_value, max_value) for value in array]


def get_max(objects: Sequence[object], field: str) -> Any:
    """Get maximum value of a field in the sequence of objects"""
    return max([getattr(o, field) for o in objects])


def get_min(objects: Sequence[object], field: str) -> Any:
    """Get minimum value of a field in the sequence of objects"""
    return min([getattr(o, field) for o in objects])
