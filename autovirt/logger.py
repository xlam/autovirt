import os
import logging


def log_dir_path(local_dir):
    logging_dir = os.path.join(os.path.normpath(os.getcwd()), local_dir)
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir


class Logger:

    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        name = kwargs.get("name", "main")
        log_dir = kwargs.get("log_dir", log_dir_path("logs"))

        if cls._instance is None:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.propagate = False

            if not logger.hasHandlers():
                filename = f"{name}.log"
                c_handler = logging.StreamHandler()
                f_handler = logging.FileHandler(os.path.join(log_dir, filename))

                c_formatter = logging.Formatter(
                    "%(asctime)s %(levelname)s (%(module)s): %(message)s"
                )
                c_handler.setFormatter(c_formatter)
                f_handler.setFormatter(c_formatter)

                logger.addHandler(c_handler)
                logger.addHandler(f_handler)

            cls._instance = logger

        return cls._instance
