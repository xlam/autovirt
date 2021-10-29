import json
import sys

import config
from autovirt import utils
from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.session import session as s


logger = utils.get_logger("virtapi.equipment")


def get_units(equipment_id: int) -> list[UnitEquipment]:
    """Get units to repair by equipment"""
    r = s.get(
        f"https://virtonomica.ru/api/vera/main/company/equipment/units"
        f"?id={config.company_id}"
        f"&product_id={equipment_id}"
        f"&pagesize={config.pagesize}"
    )
    data = json.loads(r.content)
    units = []
    for _, unit in data["data"].items():
        if float(unit["equipment_wear"]) > 0:
            units.append(
                UnitEquipment(
                    unit["id"],
                    unit["equipment_quantity"],
                    unit["equipment_quantity_max"],
                    unit["equipment_quality"],
                    unit["equipment_quality_required"],
                    unit["equipment_wear"],
                    unit["equipment_product_id"],
                )
            )
    return units


def get_offers(product_id: int) -> list[RepairOffer]:
    """Get all offers for the product"""
    r = s.get(
        f"https://virtonomica.ru/api/vera/main/company/equipment/offers"
        f"?id={config.company_id}"
        f"&product_id={product_id}"
        f"&pagesize={config.pagesize}"
    )
    if not r.ok:  # todo: move this to VirtSession
        logger.error(f"could not get offers data, response code: {r.status_code}")
    offers = []
    for _, offer in r.json()["data"].items():
        offers.append(
            RepairOffer(
                offer["id"],
                float(offer["price"]),
                float(offer["quality"]),
                int(offer["quantity"]),
            )
        )
    return offers


def repair(units: list[UnitEquipment], offer_id: str):
    """Do repair of units equpment with offer provided"""
    params = [("units_ids[]", unit.id) for unit in units]
    params.append(("id", config.company_id))
    params.append(("offer_id", offer_id))
    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/repair", params=params
    )
    if not r.ok:
        logger.error(f"could not repair, status code: {r.status_code}")
        sys.exit(0)
