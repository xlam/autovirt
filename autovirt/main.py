import argparse
import sys

from autovirt import __version__ as version
from autovirt import utils
from autovirt.exception import AutovirtError
from autovirt.session import VirtSession
from autovirt.gateway_options import GatewayOptions

config = utils.get_config("autovirt")


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="autovirt", description=f"Virtonomica automation tool (v{version})"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
        help="show version",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Do not apply changes, just show"
    )

    services = parser.add_subparsers(
        dest="service", required=True, help="Autovirt services"
    )

    # Artefact

    artefact_service = services.add_parser("artefact", help="Manage units innovations")
    artefact_actions = artefact_service.add_subparsers(
        dest="action", required=True, help="Artefact actions"
    )
    artefact_actions.add_parser("renew", help="Renew all expiring innovations")

    # Equipment

    equipment_service = services.add_parser("equipment", help="Manage equipment")
    equipment_actions = equipment_service.add_subparsers(
        dest="action", required=True, help="Equipment actions"
    )

    repair_parent = argparse.ArgumentParser(add_help=False)
    repair_parent.add_argument(
        "equipment_id", type=int, help="ID of equipment to repair"
    )
    units_group = repair_parent.add_mutually_exclusive_group()
    units_group.add_argument(
        "-u",
        "--units-only",
        type=int,
        nargs="*",
        help="ID(s) of units to repair and no more",
    )
    units_group.add_argument(
        "-e",
        "--units-exclude",
        type=int,
        nargs="*",
        help="ID(s) of units to exclude from repair",
    )

    repair = equipment_actions.add_parser(
        "repair", parents=[repair_parent], help="Repair qeuipment"
    )
    repair.add_argument(
        "-k",
        "--keep_quality",
        action="store_true",
        help="Repair by installed equipment quality instead of required",
    )

    repair_with_offer = equipment_actions.add_parser(
        "repair-with-offer",
        parents=[repair_parent],
        help="Repair qeuipment with specified offer",
    )
    repair_with_offer.add_argument(
        "-o",
        "--offer",
        type=int,
        help="Offer ID to repair with",
    )

    # Employee

    employee_service = services.add_parser("employee", help="Manage employee")
    employee_actions = employee_service.add_subparsers(
        dest="action", required=True, help="Employee actions"
    )
    employee_actions.add_parser(
        "set-required-salary", help="Set salary to required level"
    )
    employee_actions.add_parser(
        "set-demanded-salary", help="Set salary to demanded by labor union"
    )

    # Logistics

    logistics_service = services.add_parser(
        "logistics", help="Manage storages and supplies"
    )
    logistics_actions = logistics_service.add_subparsers(
        dest="action", required=True, help="logistics actions"
    )
    free_shop = logistics_actions.add_parser(
        "free-shop-storage",
        help="Free shop storage by delivering extra products to suitable warehouses",
    )
    free_shop.add_argument("shop_id", type=int, help="ID of shop")
    optimize_unit = logistics_actions.add_parser(
        "optimize-unit-supplies", help="Optimize supplies of unit"
    )
    optimize_unit.add_argument("unit_id", type=int, help="ID of unit")
    optimize_unit.add_argument(
        "-f", "--factor", type=int, default=1, help="Factor of required"
    )
    optimize_shops = logistics_actions.add_parser(
        "optimize-shops-supplies", help="Optimize supplies of all shops"
    )
    optimize_shops.add_argument(
        "-f", "--factor", type=int, default=1, help="Factor of required"
    )

    sales = services.add_parser("sales", help="Sales management")
    sales_actions = sales.add_subparsers(
        dest="action", required=True, help="Sales actions"
    )
    manage_prices = sales_actions.add_parser(
        "manage-retail-prices",
        help="Manage shop retail prices by using some tricky formula",
    )
    manage_prices.add_argument("shop_id", type=int, help="ID of shop")

    return parser.parse_args(args)


def run_artefact_renew(session, args):
    from autovirt.artefact.action.renew import RenewAction
    from autovirt.artefact.adapter.api_artefact import ApiArtefactAdapter
    from autovirt.gateway_options import GatewayOptions

    action = RenewAction(ApiArtefactAdapter(session, GatewayOptions(**config)))
    action.run(args.dry_run)


def run_employee_set_demanded_salary(session, args):
    from autovirt.employee.action.set_demanded_salary import SetDemandedSalaryAction
    from autovirt.employee.adapter.api_employee import ApiEmployeeAdapter
    from autovirt.gateway_options import GatewayOptions

    action = SetDemandedSalaryAction(
        ApiEmployeeAdapter(session, GatewayOptions(**config))
    )
    action.run(args.dry_run)


def run_employee_set_required_salary(session, args):
    from autovirt.employee.action.set_required_salary import SetRequiredSalaryAction
    from autovirt.employee.adapter.api_employee import ApiEmployeeAdapter
    from autovirt.gateway_options import GatewayOptions

    action = SetRequiredSalaryAction(
        ApiEmployeeAdapter(session, GatewayOptions(**config))
    )
    action.run(args.dry_run)


def run_equipment_repair(session, args):
    from autovirt.equipment.action.repair import RepairAction, RepairInputDTO
    from autovirt.equipment.adapter.api_equipment import ApiEquipmentAdapter

    input_dto = RepairInputDTO(
        equipment_id=args.equipment_id,
        units_only=args.units_only,
        units_exclude=args.units_exclude,
        keep_quality=args.keep_quality,
        dry_run=args.dry_run,
    )
    action = RepairAction(ApiEquipmentAdapter(session, GatewayOptions(**config)))
    action.run(input_dto)


def run_equipment_repair_with_offer(session, args):
    from autovirt.equipment.action.repair_with_offer import (
        RepairWithOfferAction,
        RepairWithOfferInputDTO,
    )
    from autovirt.equipment.adapter.api_equipment import ApiEquipmentAdapter

    input_dto = RepairWithOfferInputDTO(
        equipment_id=args.equipment_id,
        units_only=args.units_only,
        units_exclude=args.units_exclude,
        offer_id=args.offer,
        dry_run=args.dry_run,
    )
    action = RepairWithOfferAction(
        ApiEquipmentAdapter(session, GatewayOptions(**config))
    )
    action.run(input_dto)


def run_logistics_free_shop_storage(session, args):
    from autovirt.logistics.action.free_shop_storage import FreeShopStorageAction
    from autovirt.logistics.adapter.api_shop import ApiShopGateway

    action = FreeShopStorageAction(ApiShopGateway(session))
    action.run(args.shop_id, dry_run=args.dry_run)


def run_logistics_optimize_unit_supplies(session, args):
    from autovirt.logistics.action.optimize_unit_supplies import (
        OptimizeUnitSuppliesAction,
    )
    from autovirt.logistics.adapter.api_supplies import ApiSuppliesGateway

    action = OptimizeUnitSuppliesAction(ApiSuppliesGateway(session))
    action.execute(args.unit_id, factor=args.factor, dry_run=args.dry_run)


def run_logistics_optimize_shops_supplies(session, args):
    from autovirt.logistics.action.optimize_shops_supplies import (
        OptimizeShopsSuppliesAction,
    )
    from autovirt.logistics.adapter.api_supplies import ApiSuppliesGateway
    from autovirt.logistics.adapter.api_units import ApiUnitsGateway
    from autovirt.gateway_options import GatewayOptions

    gateway_options = GatewayOptions(**config)
    action = OptimizeShopsSuppliesAction(
        ApiUnitsGateway(session, gateway_options),
        ApiSuppliesGateway(session),
    )
    action.execute(factor=args.factor, dry_run=args.dry_run)


def run_sales_manage_retail_prices(session, args):
    from autovirt.sales.action.manage_retail_prices import ManageRetailPricesAction
    from autovirt.sales.adapter.api_sales import ApiSalesAdapter
    from autovirt.sales.domain import ByMiddleValue

    action = ManageRetailPricesAction(ApiSalesAdapter(session))
    action.run(args.shop_id, method=ByMiddleValue(), dry_run=args.dry_run)


modules: dict = {
    "artefact": {
        "renew": run_artefact_renew,
    },
    "employee": {
        "set-demanded-salary": run_employee_set_demanded_salary,
        "set-required-salary": run_employee_set_required_salary,
    },
    "equipment": {
        "repair": run_equipment_repair,
        "repair-with-offer": run_equipment_repair_with_offer,
    },
    "logistics": {
        "free-shop-storage": run_logistics_free_shop_storage,
        "optimize-unit-supplies": run_logistics_optimize_unit_supplies,
        "optimize-shops-supplies": run_logistics_optimize_shops_supplies,
    },
    "sales": {
        "manage-retail-prices": run_sales_manage_retail_prices,
    },
}


def dispatch(args: argparse.Namespace):
    logger = utils.init_logger(args.action)
    session = VirtSession()

    logger.info("")
    logger.info(f"CLI args: {args}")
    logger.info(f"*** Starting '{args.action}' action (dry-run: {args.dry_run}) ***")
    try:
        # run action
        modules[args.service][args.action](session, args)
    except AutovirtError as e:
        logger.error(f"{e} ({e.__class__})")
        logger.info(f"Exiting (dry-run: {args.dry_run})")
        sys.exit(1)
    logger.info(f"*** Finished '{args.action}' action (dry-run: {args.dry_run}) ***")


def run():
    # args = parse_args()
    # print(args)
    dispatch(parse_args())


if __name__ == "__main__":
    run()
