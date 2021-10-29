import os
import logging

import config


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
