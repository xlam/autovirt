from enum import Enum
from functools import reduce
from math import ceil
from typing import Optional, Tuple, Union

from autovirt import utils
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment

logger = utils.get_logger()

# maximum allowed equipment price
PRICE_MAX = 100000
# value to add and sub from offer quality when filtering
QUALITY_DELTA = 3


class QualityType(Enum):
    INSTALLED = "quality"
    REQUIRED = "quality_required"


def quantity_to_repair(units: list[UnitEquipment]) -> int:
    """Calculate total quantity of equipment to repair on given units"""
    return sum([unit.wear_quantity for unit in units])


def quantity_total(units: list[UnitEquipment]) -> int:
    """Calculate total equipment count on given units"""
    return sum([unit.quantity for unit in units])


def filter_offers(
    offers: list[RepairOffer], quality: float, quantity: int
) -> list[RepairOffer]:
    # select units in range [quality-DELTA ... quality+DELTA] and having enough repair parts
    filtered = list(filter(lambda x: x.quality > quality - QUALITY_DELTA, offers))
    filtered = list(filter(lambda x: x.quality < quality + QUALITY_DELTA, filtered))
    filtered = list(filter(lambda x: x.quantity > quantity, filtered))
    filtered = list(filter(lambda x: x.price < PRICE_MAX, filtered))
    return filtered


def expected_quality(
    qual_rep: float, qual_inst: float, items_total: int, items_wear: int
) -> float:
    return (
        qual_inst * (items_total - items_wear) + qual_rep * items_wear
    ) / items_total


def select_offer(
    offers: list[RepairOffer], units: list[UnitEquipment], quality: float = None
) -> Union[RepairOffer, None]:
    if not offers:
        return None
    if not quality:
        quality = units[0].quality_required

    qnt_rep = quantity_to_repair(units)
    qnt_total = quantity_total(units)
    qual_min = utils.get_min(units, QualityType.INSTALLED.value)
    qual_exp = [
        expected_quality(o.quality, qual_min, qnt_total, qnt_rep) for o in offers
    ]
    qual_diff = [abs(qual - quality) for qual in qual_exp]
    diff_norm = utils.normalize_array(qual_diff)
    price_norm = utils.normalize_array([o.price for o in offers])
    qp_dist = [p + q for (p, q) in zip(price_norm, diff_norm)]

    summary: list = [
        [o, price_norm[i], qual_exp[i], qual_diff[i], diff_norm[i], qp_dist[i]]
        for i, o in enumerate(offers)
        if qual_exp[i] >= quality
    ]

    if not summary:
        return None

    logger.info(f"listing filtered offers for quality of {quality}:")
    for o in summary:
        logger.info(
            f"id: {o[0].id}, quality: {o[0].quality}, price: {o[0].price},"
            f" quantity: {o[0].quantity}, qual_exp: {o[2]:.2f}, qp: {o[5]:.3f}"
        )

    minimum_qp_item = reduce(lambda x, y: x if x[5] < y[5] else y, summary)
    return minimum_qp_item[0]


def select_offer_to_raise_quality(
    unit: UnitEquipment, offers: list[RepairOffer], margin: float = 0
) -> Optional[Tuple[RepairOffer, int]]:
    required = unit.quality_required + margin
    quality_coeff = unit.quantity * (required - unit.quality)
    offers = list(filter(lambda o: o.quality >= required, offers))
    if not offers:
        return None
    offer = offers[0]
    count_to_replace = ceil(quality_coeff / (offer.quality - unit.quality))
    price = count_to_replace * offer.price
    for offer_ in offers[1:]:
        count = ceil(quality_coeff / (offer_.quality - unit.quality))
        price_ = count * offer_.price
        if price_ < price:
            offer = offer_
            count_to_replace = count
    return offer, count_to_replace


def split_by_quality(
    units: list[UnitEquipment], quality_type: QualityType = QualityType.REQUIRED
) -> dict[float, list[UnitEquipment]]:
    """Split units by quality (required or installed)"""
    res: dict[float, list[UnitEquipment]] = {}
    for unit in units:
        quality = getattr(unit, quality_type.value)
        if quality not in res.keys():
            res[quality] = []
        res[quality].append(unit)
    return res


def split_mismatch_quality_units(
    units: list[UnitEquipment],
) -> tuple[list[UnitEquipment], list[UnitEquipment]]:
    """Split units into 'normal' and 'mismatch' groups.
    Mismatched unit have installed equipment of lower quality then required.
    We need to treat them in different manner then normal while repairing.
    """
    normal = []
    mismatch = []
    for unit in units:
        if unit.quality < unit.quality_required:
            mismatch.append(unit)
        else:
            normal.append(unit)
    return normal, mismatch
