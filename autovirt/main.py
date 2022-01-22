import argparse
import sys
from typing import Protocol, Optional

from autovirt import __version__ as version
from autovirt.utils import init_logger, get_config
from autovirt.session import VirtSession
from autovirt.exception import AutovirtError


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
    session = VirtSession()
    config = get_config("autovirt")
    action: Optional[Action] = None

    if action_name == "repair":
        from autovirt.equipment import RepairAction
        from autovirt.virtapi.equipment import Equipment, EquipmentGatewayOptions

        action = RepairAction(Equipment(session, EquipmentGatewayOptions(**config)))

    if action_name == "employee":
        from autovirt.employee import SetDemandedSalaryAction
        from autovirt.virtapi.mail import VirtMailGateway
        from autovirt.virtapi.employee import (
            VirtEmployeeGateway,
            EmployeeGatewayOptions,
        )

        action = SetDemandedSalaryAction(
            VirtMailGateway(session),
            VirtEmployeeGateway(session, EmployeeGatewayOptions(**config)),
        )

    if action_name == "innovations":
        from autovirt.artefact import RenewAction
        from autovirt.virtapi.mail import VirtMailGateway
        from autovirt.virtapi.artefact import VirtArtefactGateway

        action = RenewAction(VirtMailGateway(session), VirtArtefactGateway(session))

    if action_name == "salary":
        from autovirt.employee import SetRequiredSalaryAction
        from autovirt.virtapi.employee import (
            VirtEmployeeGateway,
            EmployeeGatewayOptions,
        )

        action = SetRequiredSalaryAction(
            VirtEmployeeGateway(session, EmployeeGatewayOptions(**config))
        )

    if action:
        logger = init_logger(action_name)
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
