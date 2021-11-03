import sys

import config
from autovirt import utils
from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.session import session as s


logger = utils.get_logger()


def get_units(equipment_id: int) -> list[UnitEquipment]:
    """Get units to repair by equipment"""

    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/units",
        params={
            "id": config.company_id,
            "product_id": equipment_id,
            "pagesize": config.pagesize,
        },
    )

    units = []
    units_data = r.json()["data"].values()
    for unit in units_data:
        if float(unit["equipment_wear"]) > 0:
            units.append(
                UnitEquipment(
                    int(unit["id"]),
                    int(unit["equipment_quantity"]),
                    int(unit["equipment_quantity_max"]),
                    float(unit["equipment_quality"]),
                    float(unit["equipment_quality_required"]),
                    float(unit["equipment_wear"]),
                    int(unit["equipment_product_id"]),
                )
            )

    return units


def get_offers(product_id: int) -> list[RepairOffer]:
    """Get all offers for the product"""

    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/offers",
        params={
            "id": config.company_id,
            "product_id": product_id,
            "pagesize": config.pagesize,
        },
    )
    if not r.ok:  # todo: move this to VirtSession
        logger.error(f"could not get offers data, response code: {r.status_code}")

    offers = []
    offers_data = r.json()["data"].values()
    for offer in offers_data:
        offers.append(
            RepairOffer(
                int(offer["id"]),
                float(offer["price"]),
                float(offer["quality"]),
                int(offer["quantity"]),
            )
        )

    return offers


def repair(units: list[UnitEquipment], offer: RepairOffer):
    """Do repair of units equpment with offer provided"""

    params = [("units_ids[]", unit.id) for unit in units]
    params.append(("id", config.company_id))
    params.append(("offer_id", offer.id))
    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/repair", params=params
    )
    if not r.ok:
        logger.error(f"could not repair, status code: {r.status_code}")
        sys.exit(0)
