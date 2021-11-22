import sys
from functools import reduce
from math import ceil
from typing import Tuple, Optional

import config
from autovirt import utils
from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.virtapi import equipment

logger = utils.get_logger()


def quantity_to_repair(units: list[UnitEquipment]) -> int:
    """Calculate total quantity of equipment to repair on given units"""
    return reduce(lambda a, unit: a + unit.wear_quantity, units, 0)


def quantity_total(units: list[UnitEquipment]) -> int:
    """Calculate total equipment count on given units"""
    return reduce(lambda a, unit: a + unit.qnt, units, 0)


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

    qual_min = utils.get_min(units, "qual")
    qual_exp = [
        expected_quality(o.quality, qual_min, qnt_total, qnt_rep) for o in offers
    ]
    qual_diff = [abs(qual - quality) for qual in qual_exp]
    diff_min = min(qual_diff)
    diff_max = max(qual_diff)
    diff_norm = [utils.normalize(diff, diff_min, diff_max) for diff in qual_diff]

    price_min = utils.get_min(offers, "price")
    price_max = utils.get_max(offers, "price")
    price_norm = [utils.normalize(o.price, price_min, price_max) for o in offers]

    qp_dist = [p + q for (p, q) in zip(price_norm, diff_norm)]

    summary = [
        [o, price_norm[i], qual_exp[i], qual_diff[i], diff_norm[i], qp_dist[i]]
        for i, o in enumerate(offers)
    ]

    filtered = list(filter(lambda item: item[2] >= quality, summary))

    logger.info(f"listing filtered offers for quality of {quality}:")
    for o in filtered:
        logger.info(
            f"id: {o[0].id}, quality: {o[0].quality}, price: {o[0].price},"
            f" quantity: {o[0].quantity}, qual_exp: {o[2]}, qp: {o[5]}"
        )

    offer = filtered[0][0]
    qp = filtered[0][5]
    for x in filtered:
        if x[5] < qp:
            qp = x[5]
            offer = x[0]

    return offer


def select_offer_to_raise_quality(
    unit: UnitEquipment, offers: list[RepairOffer]
) -> Optional[Tuple[RepairOffer, int]]:
    quality_coeff = unit.qnt * (unit.qual_req - unit.qual)
    offers = list(filter(lambda o: o.quality >= unit.qual_req, offers))
    if not offers:
        return
    offer = offers[0]
    count_to_replace = ceil(quality_coeff / (offer.quality - unit.qual))
    price = count_to_replace * offer.price
    for offer_ in offers[1:]:
        count = ceil(quality_coeff / (offer_.quality - unit.qual))
        price_ = count * offer_.price
        if price_ < price:
            offer = offer_
            count_to_replace = count
    return offer, count_to_replace


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


def split_mismatch_quality_units(
    units: list[UnitEquipment], quality: float
) -> tuple[list[UnitEquipment], list[UnitEquipment]]:
    """Split units into 'normal' and 'mismatch' groups.
    Mismatched unit have installed equipment of lower quality then required.
    We need to treat them in different manner then normal while repairing.
    """
    normal = []
    mismatch = []
    for unit in units:
        if unit.qual < quality:
            mismatch.append(unit)
        else:
            normal.append(unit)
    return normal, mismatch


def repair_with_quality(
    units: list[UnitEquipment], equipment_id: int, quality: float
) -> float:
    units_normal, units_mismatch = split_mismatch_quality_units(units, quality)
    if units_mismatch:
        logger.info("mismatch units qualities found, skipping them:")
        logger.info(units_mismatch)
    quantity = quantity_to_repair(units_normal)
    offers = equipment.get_offers(equipment_id)
    offer = select_offer(offers, units_normal, quality)
    repair_cost = quantity * offer.price
    logger.info(
        f"found offer {offer.id} with quality {offer.quality} "
        f"and price {offer.price} (repair cost: {repair_cost})"
    )
    logger.info(
        f"repairing {quantity} pieces of quality {quality} " f"on {len(units)} units"
    )
    equipment.repair(units_normal, offer)
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
