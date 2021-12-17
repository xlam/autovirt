import argparse
import importlib
from autovirt import __version__ as version
from autovirt.utils import init_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str)
    parser.add_argument("-c, --config", type=str, dest="config", default=None)
    return parser.parse_args()


def run():
    print(f"Running autovirt version {version}")
    args = parse_args()
    print("args: ", args)
    action_name = args.action
    action_config = args.config

    logger = init_logger(action_name)
    logger.info("")
    logger.info(f"*** starting '{action_name}' action ***")

    action_module = ".".join(["autovirt.action", action_name])
    action = importlib.import_module(action_module)
    action.run(action_config)  # type: ignore


if __name__ == "__main__":
    run()
