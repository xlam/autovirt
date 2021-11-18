import sys
from functools import reduce

import config
from autovirt import utils
from autovirt.virtapi import equipment
from autovirt.structs import UnitEquipment, RepairOffer


logger = utils.get_logger()


def quantity_to_repair(units: list[UnitEquipment]) -> int:
    """Calculate total quantity of equipment to repair on given units"""
    return reduce(lambda a, unit: a + unit.wear_quantity, units, 0)


def quantity_total(units: list[UnitEquipment]) -> int:
    """Calculate total equipment count on given units"""
    return reduce(lambda a, unit: a + unit.qnt, units, 0)


def get_max(objects: list[object], field: str):
    return reduce(
        lambda x, y: max([x, getattr(y, field)]), objects, getattr(objects[0], field)
    )


def get_min(objects: list[object], field: str):
    return reduce(
        lambda x, y: min([x, getattr(y, field)]), objects, getattr(objects[0], field)
    )


def filter_offers(
    offers: list[RepairOffer], quality: float, quantity: int
) -> list[RepairOffer]:
    # select units in range [quality-2 ... quality+3] and having enough repair parts
    filtered = list(filter(lambda x: x.quality > quality - 3, offers))
    filtered = list(filter(lambda x: x.quality < quality + 3, filtered))
    filtered = list(filter(lambda x: x.quantity > quantity, filtered))
    filtered = list(filter(lambda x: x.price < 100000, filtered))
    return filtered


def expected_quality(
    qual_rep: float, qual_inst: float, items_total: int, items_wear: int
) -> float:
    return (
        qual_inst * (items_total - items_wear) + qual_rep * items_wear
    ) / items_total


def select_offer(
    offers: list[RepairOffer], units: list[UnitEquipment], quality: float = None
) -> RepairOffer:
    if not quality:
        quality = units[0].qual_req
    qnt_rep = quantity_to_repair(units)
    qnt_total = quantity_total(units)
    offers = filter_offers(offers, quality, qnt_rep)

    qual_min = get_min(units, "qual")
    qual_exp = [
        expected_quality(o.quality, qual_min, qnt_total, qnt_rep) for o in offers
    ]
    qual_diff = [abs(qual - quality) for qual in qual_exp]
    diff_min = min(qual_diff)
    diff_max = max(qual_diff)
    diff_norm = [utils.normalize(diff, diff_min, diff_max) for diff in qual_diff]

    price_min = get_min(offers, "price")
    price_max = get_max(offers, "price")
    price_norm = [utils.normalize(o.price, price_min, price_max) for o in offers]

    qp_dist = [p + q for (p, q) in zip(price_norm, diff_norm)]

    summary = [
        [o, price_norm[i], qual_exp[i], qual_diff[i], diff_norm[i], qp_dist[i]]
        for i, o in enumerate(offers)
    ]

    filtered = list(filter(lambda x: x[2] >= quality, summary))
    offer = filtered[0][0]
    qp = filtered[0][5]
    for x in filtered:
        if x[5] < qp:
            qp = x[5]
            offer = x[0]

    return offer


def find_offer(offers: list[RepairOffer], quality: float, quantity: int) -> RepairOffer:
    """Find best offer with required quality and enough quantity"""

    logger.info(f"filtering offers of quality {quality} and quantity {quantity}")
    filtered = filter_offers(offers, quality, quantity)
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


def repair_with_quality(
    units: list[UnitEquipment], equipment_id: int, quality: float
) -> float:
    quantity = quantity_to_repair(units)
    offers = equipment.get_offers(equipment_id)
    # offer = find_offer(offers, quality, quantity)
    offer = select_offer(offers, units, quality)
    repair_cost = quantity * offer.price
    logger.info(
        f"found offer {offer.id} with quality {offer.quality} "
        f"and price {offer.price} (repair cost: {repair_cost})"
    )
    logger.info(
        f"repairing {quantity} pieces of quality {quality} " f"on {len(units)} units"
    )
    equipment.repair(units, offer)
    return repair_cost


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
        for quality, units_list in units.items():
            repair_cost = repair_with_quality(units_list, equipment_id, quality)
            total_cost += repair_cost

    logger.info(f"total repair cost: {total_cost}")
    logger.info("repairing finished")
