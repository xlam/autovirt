import sys

import config
from autovirt import utils
from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.session import token, session as s


logger = utils.get_logger()


def fetch_units(equipment_id: int) -> list[dict]:
    """Fetch units equipment data"""
    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/units",
        params={
            "id": config.company_id,
            "product_id": equipment_id,
            "pagesize": config.pagesize,
        },
    )
    return r.json()["data"].values()


def fetch_offers(product_id: int) -> list[dict]:
    """Fetch offers by product id"""
    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/equipment/offers",
        params={
            "id": config.company_id,
            "product_id": product_id,
            "pagesize": config.pagesize,
        },
    )
    return r.json()["data"].values()


def get_units(equipment_id: int) -> list[UnitEquipment]:
    """Get units to repair by equipment.
    Only units whose equipment wear in greater then 0% will be returned
    """
    units_data = fetch_units(equipment_id)
    units = []
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
    offers_data = fetch_offers(product_id)
    offers = []
    for offer in offers_data:
        offers.append(
            RepairOffer(
                int(offer["id"]),
                int(offer["company_id"]),
                str(offer["company_name"]),
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
    r = s.post(
        "https://virtonomica.ru/api/vera/main/company/equipment/repair", params=params
    )
    logger.info(f"Virtonomica API response: {r.json()}")
    if not r.ok:
        logger.error(f"could not repair, status code: {r.status_code}")
        sys.exit(0)


def terminate(unit: UnitEquipment, quantity: int):
    r = s.post(
        "https://virtonomica.ru/api/vera/main/unit/equipment/terminate",
        {
            "id": unit.id,
            "token": token,
            "qty": quantity,
        },
    )
    if not r.ok:
        logger.error(f"could not terminate equipment, status code: {r.status_code}")
        sys.exit(0)


def buy(unit: UnitEquipment, offer: RepairOffer, quantity: int):
    r = s.post(
        "https://virtonomica.ru/api/vera/main/unit/equipment/update",
        {
            "offer_id": offer.id,
            "id": unit.id,
            "token": token,
            "operation_name": "buy",
            "equipment_count": quantity,
        },
    )
    if not r.ok:
        logger.error(f"could not buy equipment, status code: {r.status_code}")
        sys.exit(0)
