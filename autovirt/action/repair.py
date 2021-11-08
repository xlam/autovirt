import sys

import config
from autovirt import utils
from autovirt.virtapi import equipment
from autovirt.structs import UnitEquipment, RepairOffer


logger = utils.get_logger()


def quantity_to_repair(units: list[UnitEquipment]) -> int:
    """Calculate total quantity of equipment to repair"""
    quantity = 0
    for unit in units:
        quantity += unit.wear_quantity
    return quantity


def find_offer(offers: list[RepairOffer], quality: float, quantity: int) -> RepairOffer:
    """Find best offer with required quality and enough quantity"""

    logger.info(f"filtering offers of quality {quality} and quantity {quantity}")

    # select units in range [quality-2 ... quality+3] and having enough repair parts
    filtered = list(filter(lambda x: x.quality > quality - 2, offers))
    filtered = list(filter(lambda x: x.quality < quality + 3, filtered))
    filtered = list(filter(lambda x: x.quantity > quantity, filtered))

    if not filtered:
        logger.info("could not select supplier by criteria, exiting...")
        sys.exit(0)

    logger.info(f"listing filtered offers for quality of {quality}:")
    for o in filtered:
        logger.info(
            f"id: {o.id}, quality: {o.quality}, price: {o.price}, quantity: {o.quantity}, qp: {o.qp_ratio}"
        )

    # select one with highest quality/price ratio (mostly cheaper one)
    res = filtered[0]
    for offer in filtered:
        if offer.qp_ratio > res.qp_ratio:
            res = offer

    return res


def get_offers_by_quality(
    units: dict[float, list[UnitEquipment]], offers: list[RepairOffer]
) -> dict[RepairOffer, list[UnitEquipment]]:
    """Find best offers for groups of units by quality"""
    res = {}
    logger.info(f"getting offers for qualities {list(units.keys())}")
    for (quality, units_list) in units.items():
        logger.info(f"getting offer for quality {quality} ({len(units_list)} units)")
        quantity = quantity_to_repair(units_list)
        offer = find_offer(offers, quality, quantity)
        logger.info(f"got offer: {offer.id}")
        if offer not in res:
            res[offer] = units_list
        else:
            res[offer] = res[offer] + units_list
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

    logger.info(f"starting repair equipment id {equipment_id}")

    total_cost = 0

    if config.Option.exclude in options:
        excludes = repair_config[config.Option.exclude]
        units = [unit for unit in units for ex in excludes if unit.id != ex]
    if config.Option.include in options:
        includes = repair_config[config.Option.include]
        units = [unit for unit in units for inc in includes if unit.id == inc]

    if config.Option.offer_id in options:
        quantity = quantity_to_repair(units)
        offers = equipment.get_offers(equipment_id)
        offer_id = repair_config[config.Option.offer_id]
        offer = [o for o in offers if o.id == offer_id][0]
        total_cost = quantity * offer.price
        logger.info(f"repairing {quantity} pieces on {len(units)} units")
        logger.info(
            f"using offer {offer.id} with quality {offer.quality} "
            f"and price {offer.price} (repair cost: {total_cost})"
        )
        equipment.repair(units, offer)
    else:
        quality_type = "qual_req"
        if config.Option.quality in options:
            quality_type = "qual"
        units = split_by_quality(units, quality_type=quality_type)
        logger.info(
            f"prepared units with {len(units)} quality levels: {list(units.keys())}"
        )
        offers = get_offers_by_quality(units, equipment.get_offers(equipment_id))

        for offer, units in offers.items():
            if quality_type == "qual_req":
                quality = units[0].qual_req
            else:
                quality = units[0].qual
            quantity = quantity_to_repair(units)
            repair_cost = quantity * offer.price
            total_cost += repair_cost
            logger.info(
                f"repairing {quantity} pieces of quality {quality} "
                f"on {len(units)} units"
            )
            logger.info(
                f"using offer {offer.id} with quality {offer.quality} "
                f"and price {offer.price} (repair cost: {repair_cost})"
            )
            equipment.repair(units, offer)

    logger.info(f"total repair cost: {total_cost}")
    logger.info("repairing finished")
