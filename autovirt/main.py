import argparse
import sys
from typing import Protocol, Optional

from autovirt import __version__ as version
from autovirt import utils
from autovirt.exception import AutovirtError
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


class Action(Protocol):
    def run(self, config_name: str):
        pass


def dispatch(action_name: str, action_options: str):
    logger = utils.init_logger(action_name)
    session = VirtSession()
    config = utils.get_config("autovirt")
    action: Optional[Action] = None

    if action_name == "repair":
        from autovirt.equipment import RepairAction
        from autovirt.virtapi.equipment import VirtEquipment
        from autovirt.virtapi import GatewayOptions

        action = RepairAction(VirtEquipment(session, GatewayOptions(**config)))

    if action_name == "employee":
        from autovirt.employee.action import SetDemandedSalaryAction
        from autovirt.employee.adapter import UnitSalaryAdapter
        from autovirt.virtapi import GatewayOptions

        action = SetDemandedSalaryAction(
            UnitSalaryAdapter(session, GatewayOptions(**config)),
        )

    if action_name == "salary":
        from autovirt.employee.action import SetRequiredSalaryAction
        from autovirt.employee.adapter import VirtEmployee
        from autovirt.virtapi import GatewayOptions

        action = SetRequiredSalaryAction(
            VirtEmployee(session, GatewayOptions(**config))
        )

    if action_name == "innovations":
        from autovirt.artefact import RenewAction
        from autovirt.virtapi.mail import VirtMail
        from autovirt.virtapi.artefact import VirtArtefact

        action = RenewAction(VirtMail(session), VirtArtefact(session))

    if action:
        logger.info("")
        logger.info(f"*** starting '{action_name}' action ***")
        try:
            action.run(action_options)
        except AutovirtError as e:
            logger.error(f"{e} ({e.__class__})")
            logger.info("exiting.")
            sys.exit(1)
        logger.info(f"*** finished '{action_name}' action ***")


def run():
    args = parse_args()
    dispatch(args.action, args.config)


if __name__ == "__main__":
    run()
