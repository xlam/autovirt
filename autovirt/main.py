import argparse
import sys

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


def dispatch(action_name: str, action_options: str):
    logger = utils.init_logger(action_name)
    session = VirtSession()
    config = utils.get_config("autovirt")
    action = None

    # Quick walk-around for passing different arguments to actions run() method
    params = []

    if action_name == "repair":
        from autovirt.equipment.action import RepairAction, RepairInputDTO
        from autovirt.equipment.adapter.api_equipment import ApiEquipmentAdapter
        from autovirt.gateway_options import GatewayOptions

        def get_repair_config(config_section: str) -> dict:
            repair_config = utils.get_config("repair")
            try:
                repair_options = repair_config[config_section]
            except KeyError:
                raise AutovirtError(f"configuration '{config_section}' not found!")
            return repair_options

        input_dto = RepairInputDTO(**get_repair_config(action_options))
        params = [input_dto]
        action = RepairAction(ApiEquipmentAdapter(session, GatewayOptions(**config)))

    if action_name == "employee":
        from autovirt.employee.action import SetDemandedSalaryAction
        from autovirt.employee.adapter import ApiEmployeeAdapter
        from autovirt.gateway_options import GatewayOptions

        action = SetDemandedSalaryAction(  # type: ignore
            ApiEmployeeAdapter(session, GatewayOptions(**config)),
        )

    if action_name == "salary":
        from autovirt.employee.action import SetRequiredSalaryAction
        from autovirt.employee.adapter import ApiEmployeeAdapter
        from autovirt.gateway_options import GatewayOptions

        action = SetRequiredSalaryAction(  # type: ignore
            ApiEmployeeAdapter(session, GatewayOptions(**config))
        )

    if action_name == "innovations":
        from autovirt.artefact.action import RenewAction
        from autovirt.artefact.adapter import ApiArtefactAdapter
        from autovirt.gateway_options import GatewayOptions

        action = RenewAction(ApiArtefactAdapter(session, GatewayOptions(**config)))  # type: ignore

    if action:
        logger.info("")
        logger.info(f"*** starting '{action_name}' action ***")
        try:
            action.run(*params)
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
