import argparse

from autovirt import __version__ as version
from autovirt.utils import init_logger, get_config
from autovirt.session import VirtSession


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Autovirt", description=f"Virtonomica automation tool (v{version})"
    )
    parser.add_argument(
        "action", type=str, choices=["repair", "innovations", "salary", "employee"]
    )
    parser.add_argument(
        "-c, --config",
        type=str,
        dest="config",
        default=None,
        help="configuration section of autovirt.toml for specified action. ",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
        help="show version",
    )
    return parser.parse_args()


def dispatch(action_name: str, action_options: str):
    session = VirtSession()
    config = get_config("autovirt")
    action = None
    if action_name == "repair":
        from autovirt.action.repair import RepairAction
        from autovirt.virtapi.equipment import Equipment, EquipmentGatewayOptions

        action = RepairAction(Equipment(session, EquipmentGatewayOptions(**config)))

    if action:
        logger = init_logger(action_name)
        logger.info("")
        logger.info(f"*** starting '{action_name}' action ***")
        action.run(action_options)


def run():
    args = parse_args()
    dispatch(args.action, args.config)


if __name__ == "__main__":
    run()
