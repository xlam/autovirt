import argparse
import importlib
from autovirt import __version__ as version


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str)
    parser.add_argument("-c, --config", type=str, dest="config", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    print(f"Running autovirt version {version}")
    args = parse_args()
    print("args: ", args)
    action_name = args.action
    action_config = args.config

    action_module = ".".join(["autovirt.action", action_name])
    action = importlib.import_module(action_module)
    action.run(action_config)