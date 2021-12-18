import sys

import tomli

_config = None

CONFIG_FILENAME = "autovirt.toml"


def config() -> dict:
    global _config
    if not _config:
        with open(CONFIG_FILENAME, "rb") as f:
            try:
                _config = tomli.load(f)
            except tomli.TOMLDecodeError as e:
                print(f"Error: {CONFIG_FILENAME} parsing error: {e}")
                sys.exit(1)
    return _config
