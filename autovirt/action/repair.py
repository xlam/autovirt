import sys

import config
from autovirt import utils
from autovirt.virtapi import equipment
from autovirt.structs import UnitEquipment, RepairOffer


logger = utils.get_logger()
logger.info("starting repair")


def quantity_to_repair(units: list[UnitEquipment]) -> int:
    """Calculate total quantity of equipment to repair"""
    quantity = 0
    for unit in units:
        quantity += unit.wear_quantity
    return quantity


def get_offer(equipment_id: str, quality: float, quantity: int) -> RepairOffer:
    """Find best offer with required quality and enough quantity"""
    offers = equipment.get_offers(int(equipment_id))

    # select units in range [quality-2 ... quality+3] and having enough repair parts
    offers = list(filter(lambda x: int(x.quality) > quality - 2, offers))
    offers = list(filter(lambda x: int(x.quality) < quality + 3, offers))
    offers = list(filter(lambda x: int(x.quantity) > quantity, offers))

    if not offers:
        logger.info("could not select supplier by criteria, exiting...")
        sys.exit(0)

    # select one with highest quality/price ratio (mostly cheaper one)
    res = offers[0]
    for offer in offers:
        if (offer.quality / offer.price) > (res.quality / res.price):
            res = offer

    return res


def get_offers_by_quality(
    units: dict[float, list[UnitEquipment]], equipment_id: str
) -> dict[RepairOffer, list[UnitEquipment]]:
    """Find best offers for groups of units by quality"""
    res = {}
    for (quality, units_list) in units.items():
        quantity = quantity_to_repair(units_list)
        offer = get_offer(equipment_id, quality, quantity)
        res[offer] = units_list
    return res


def split_by_quality(
    units: list[UnitEquipment], quality_type: str = "qual_req"
) -> dict[float, list[UnitEquipment]]:
    """Split units by quality (required or installed)"""
    res: dict[float, list[UnitEquipment]] = {}
    for unit in units:
        quality = getattr(unit, quality_type)
        if quality not in res.keys():
            res[quality] = []
        res[quality].append(unit)
    return res


def run(config_name):
    if not config_name or config_name not in config.repair.keys():
        logger.error(f"config '{config_name}' does not exist, exiting")
        sys.exit(1)

    repair_config = config.repair[config_name]
    options = repair_config.keys()
    equipment_id = repair_config[config.Option.equip_id]
    units = equipment.get_units(equipment_id)

    if not units:
        logger.info("nothing to repair, exiting")
        sys.exit(0)

    if config.Option.exclude in options:
        excludes = repair_config[config.Option.exclude]
        units = [unit for unit in units for ex in excludes if int(unit.id) != ex]
    if config.Option.include in options:
        includes = repair_config[config.Option.include]
        units = [unit for unit in units for inc in includes if int(unit.id) == inc]
    if config.Option.supplier in options:
        quantity = quantity_to_repair(units)
        logger.info(
            f"repairing {quantity} pieces (id: {equipment_id}) "
            f"on {len(units)} units..."
        )
        equipment.repair(units, repair_config[config.Option.supplier])
    else:
        quality_type = "qual_req"
        if config.Option.quality in options:
            quality_type = "qual"
        units = split_by_quality(units, quality_type=quality_type)
        logger.info(f"prepared units dict with {len(units)} quality levels:")
        logger.info(units.keys())
        offers = get_offers_by_quality(units, equipment_id)
        for (offer, units) in offers.items():
            quantity = quantity_to_repair(units)
            logger.info(
                f"repairing {quantity} pieces (id: {equipment_id}) "
                f"on {len(units)} units..."
            )
            equipment.repair(units, offer)

    logger.info("repairing finished")
