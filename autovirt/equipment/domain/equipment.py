from dataclasses import dataclass
from enum import Enum
from functools import reduce
from math import ceil
from typing import Optional, Tuple, Union

from autovirt import utils
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment

# maximum allowed equipment price
PRICE_MAX = 100000
# value to add and sub from offer quality when filtering
QUALITY_DELTA = 3


@dataclass
class FilteredOffer:
    offer: RepairOffer
    cost_norm: float
    qual_exp: float
    qual_diff: float
    diff_norm: float
    qp_dist: float


class EquipmentInstrumentation:
    def __init__(self):
        self.logger = utils.get_logger()


class SelectOfferInstrumentation(EquipmentInstrumentation):
    def offers_filtered(self, filtered_offers: list[FilteredOffer], quality):
        self.logger.info(f"Listing filtered offers for quality of {quality:.2f}:")
        for f in filtered_offers:
            self.logger.info(
                f"id: {f.offer.id}, quality: {f.offer.quality:.2f}, cost: {f.offer.cost:.2f},"
                f" quantity: {f.offer.quantity}, qual_exp: {f.qual_exp:.3f}, qp: {f.qp_dist:.3f}"
            )

    def no_offers_found_to_repair(self, units: list[UnitEquipment], quality):
        self.logger.warning(
            f"Could not select offer to repair quality {quality:.2f} on {len(units)} units"
        )

    def found_offer_to_repair(self, offer: RepairOffer, quantity: int):
        self.logger.info(
            f"Found offer {offer.id} with quality {offer.quality:.2f} "
            f"and price {offer.cost:.2f} (repair cost: {offer.cost * quantity:.2f})"
        )


class SelectOfferToRaiseQualityInstrumentation(EquipmentInstrumentation):
    def no_offers_found_to_fix(self, unit: UnitEquipment):
        self.logger.info(
            f"No offers found to fix unit {unit.id} "
            f"(installed quality: {unit.quality_installed:.2f}, required: {unit.quality_required:.2f}), skipping"
        )

    def found_offer_to_fix(
        self, unit: UnitEquipment, offer: RepairOffer, quantity_to_replace: int
    ):
        self.logger.info(
            f"Found offer {offer.id} (quality: {offer.quality:.2f}, price: {offer.cost:.2f}) "
            f"to replace {quantity_to_replace} items at unit {unit.id} "
            f"(installed quality: {unit.quality_installed:.2f}, required: {unit.quality_required:.2f})"
        )


class SplitMismatchQualityInstrumentation(EquipmentInstrumentation):
    def units_splitted(
        self, mismatch: list[UnitEquipment], normal: list[UnitEquipment]
    ):
        if mismatch:
            self.logger.info("Found units with quality lower then required:")
            self.logger.info(mismatch)
            self.logger.info("Fixing mismatched units...")
        if not normal:
            self.logger.info("Nothing to repair, exiting")


class QualityType(Enum):
    INSTALLED = "quality_installed"
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
    filtered = list(filter(lambda x: x.cost < PRICE_MAX, filtered))
    return filtered


def expected_quality(
    qual_rep: float, qual_inst: float, items_total: int, items_wear: int
) -> float:
    return (
        qual_inst * (items_total - items_wear) + qual_rep * items_wear
    ) / items_total


def select_offer(
    offers: list[RepairOffer],
    units: list[UnitEquipment],
    quality: Union[float, None] = None,
) -> Union[RepairOffer, None]:
    instrumentation = SelectOfferInstrumentation()

    if not offers:
        instrumentation.no_offers_found_to_repair(units, quality)
        return None

    if not quality:
        quality = units[0].quality_required

    # calculate all relevant values
    qnt_repair = quantity_to_repair(units)
    qnt_total = quantity_total(units)
    qual_min = utils.get_min(units, QualityType.INSTALLED.value)
    qual_exp = [
        expected_quality(o.quality, qual_min, qnt_total, qnt_repair) for o in offers
    ]
    qual_diff = [abs(qual - quality) for qual in qual_exp]
    diff_norm = utils.normalize_array(qual_diff)
    cost_norm = utils.normalize_array([o.cost for o in offers])
    qp_dist = [p + q for (p, q) in zip(cost_norm, diff_norm)]

    summary = [
        FilteredOffer(
            o, cost_norm[i], qual_exp[i], qual_diff[i], diff_norm[i], qp_dist[i]
        )
        for i, o in enumerate(offers)
        if qual_exp[i] >= quality
    ]

    if not summary:
        instrumentation.no_offers_found_to_repair(units, quality)
        return None
    instrumentation.offers_filtered(summary, quality)

    minimum_qp_item = reduce(lambda x, y: x if x.qp_dist < y.qp_dist else y, summary)
    instrumentation.found_offer_to_repair(minimum_qp_item.offer, qnt_repair)
    return minimum_qp_item.offer


def select_offer_to_raise_quality(
    unit: UnitEquipment, offers: list[RepairOffer], margin: float = 0
) -> Tuple[Optional[RepairOffer], Optional[int]]:
    instrumentation = SelectOfferToRaiseQualityInstrumentation()

    quality_required = unit.quality_required + margin
    quality_coeff = unit.quantity * (quality_required - unit.quality_installed)

    # calculates equipment quantity to replace with given offer
    def calc_quantity(offer_: RepairOffer) -> int:
        return ceil(quality_coeff / (offer_.quality - unit.quality_installed))

    offers = list(filter(lambda o: o.quality >= quality_required, offers))
    offers = list(filter(lambda o: o.quantity >= calc_quantity(o), offers))
    if not offers:
        instrumentation.no_offers_found_to_fix(unit)
        return None, None

    selected_offer = offers[0]
    quantity_to_replace = calc_quantity(selected_offer)
    total_cost = quantity_to_replace * selected_offer.cost
    for offer in offers[1:]:
        quantity = calc_quantity(offer)
        cost = quantity * offer.cost
        if cost < total_cost:
            selected_offer = offer
            quantity_to_replace = quantity
    instrumentation.found_offer_to_fix(unit, selected_offer, quantity_to_replace)
    return selected_offer, quantity_to_replace


def split_by_quality(
    units: list[UnitEquipment], quality_type: QualityType = QualityType.REQUIRED
) -> dict[float, list[UnitEquipment]]:
    """Split units by quality (required or installed)"""
    res: dict[float, list[UnitEquipment]] = {}
    for unit in units:
        quality = getattr(unit, str(quality_type.value))
        if quality not in res.keys():
            res[quality] = []
        res[quality].append(unit)
    return res


def split_mismatch_required_quality_units(
    units: list[UnitEquipment],
) -> tuple[list[UnitEquipment], list[UnitEquipment]]:
    """Split units into 'normal' and 'mismatch' groups.
    Mismatched unit have installed equipment of lower quality then required.
    We need to treat them in different manner then normal while repairing.
    """

    instrumentation = SplitMismatchQualityInstrumentation()

    normal = []
    mismatch = []
    for unit in units:
        if unit.quality_installed < unit.quality_required:
            mismatch.append(unit)
        else:
            normal.append(unit)
    instrumentation.units_splitted(mismatch, normal)
    return normal, mismatch
