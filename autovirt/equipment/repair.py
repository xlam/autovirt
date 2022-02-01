import sys
from typing import Optional

from pydantic import BaseModel

from autovirt import utils
from autovirt.equipment.domain.equipment import (
    QualityType,
    quantity_to_repair,
    select_offer,
    select_offer_to_raise_quality,
    split_by_quality,
    split_mismatch_quality_units,
)
from autovirt.equipment.interface import EquipmentGateway
from autovirt.exception import AutovirtError
from autovirt.structs import UnitEquipment

logger = utils.get_logger()


class RepairConfig(BaseModel):
    equipment_id: int
    include: Optional[list[int]] = None
    exclude: Optional[list[int]] = None
    offer_id: Optional[int] = None
    quality: Optional[bool] = None


class RepairAction:
    def __init__(
        self, equipment_gateway: EquipmentGateway, options: Optional[dict] = None
    ):
        self.options = utils.get_config("repair") if not options else options
        self.equipment = equipment_gateway

    def fix_units_quality(self, units: list[UnitEquipment], margin: float = 0):
        for unit in units:
            # need to update offers before each operation
            offers = self.equipment.get_offers(unit.equipment_id)
            res = select_offer_to_raise_quality(unit, offers, margin)
            if not res:
                logger.info(
                    f"no offers found to fix unit {unit.id} "
                    f"(installed quality: {unit.quality}, required: {unit.quality_required}), skipping"
                )
                continue
            (offer, quantity) = res
            logger.info(
                f"got offer {offer.id} (quality: {offer.quality}, price: {offer.price}) "
                f"to replace {quantity} items at unit {unit.id} "
                f"(installed quality: {unit.quality}, required: {unit.quality_required})"
            )
            self.equipment.terminate(unit, quantity)
            self.equipment.buy(unit, offer, quantity)

    def repair_with_quality(self, units: list[UnitEquipment], quality: float) -> float:
        units_normal, units_mismatch = split_mismatch_quality_units(units)
        if units_mismatch:
            logger.info("mismatch units qualities found, fixing them:")
            logger.info(units_mismatch)
            self.fix_units_quality(units_mismatch)
        if not units_normal:
            logger.info("nothing to repair, exiting")
            sys.exit(0)
        quantity = quantity_to_repair(units_normal)
        offers = self.equipment.get_offers(units_normal[0].equipment_id)
        try:
            offer = select_offer(offers, units_normal, quality)
        except AutovirtError as e:
            logger.error(e)
            return 0.0
        repair_cost = quantity * offer.price
        logger.info(
            f"found offer {offer.id} with quality {offer.quality} "
            f"and price {offer.price} (repair cost: {repair_cost:.0f})"
        )
        logger.info(
            f"repairing {quantity} pieces of quality {quality} on {len(units)} units"
        )
        self.equipment.repair(units_normal, offer)
        return repair_cost

    def get_repair_config(self, config_name: str) -> dict:
        try:
            repair_config = self.options[config_name]
        except KeyError:
            raise AutovirtError(f"configuration '{config_name}' not found!")
        return repair_config  # type: ignore

    @staticmethod
    def filter_units_with_exclude_and_include_options(
        units: list[UnitEquipment], repair_config: RepairConfig
    ) -> list[UnitEquipment]:
        if repair_config.exclude:
            excludes = repair_config.exclude
            units = [unit for unit in units for ex in excludes if unit.id != ex]
        if repair_config.include:
            includes = repair_config.include
            units = [unit for unit in units for inc in includes if unit.id == inc]
        return units

    def repair_by_quality(self, units: list[UnitEquipment], quality_type: QualityType):
        units_ = split_by_quality(units, quality_type=quality_type)
        logger.info(
            f"prepared units with {len(units_)} quality levels: {list(units_.keys())}"
        )
        total_cost = 0.0
        for quality, units_list in units_.items():
            repair_cost = self.repair_with_quality(units_list, quality)
            total_cost += repair_cost
        logger.info(f"total repair cost: {total_cost:.0f}")

    def repair_with_config_offer(
        self, units: list[UnitEquipment], offer_id: int
    ) -> float:
        quantity = quantity_to_repair(units)
        offers = self.equipment.get_offers(units[0].equipment_id)
        offer = [o for o in offers if o.id == offer_id][0]
        total_cost = quantity * offer.price
        logger.info(f"repairing {quantity} pieces on {len(units)} units")
        logger.info(
            f"using offer {offer.id} with quality {offer.quality} "
            f"and price {offer.price} (repair cost: {total_cost:.0f})"
        )
        self.equipment.repair(units, offer)
        return total_cost

    def run(self, config_name: str):
        repair_config = RepairConfig(**self.get_repair_config(config_name))

        logger.info(f"starting repair equipment id {repair_config.equipment_id}")
        units = self.equipment.get_units_to_repair(repair_config.equipment_id)
        units = self.filter_units_with_exclude_and_include_options(units, repair_config)

        if not units:
            logger.info("nothing to repair, exiting")
            sys.exit(0)

        if repair_config.offer_id:
            self.repair_with_config_offer(units, repair_config.offer_id)
        else:
            quality_type = (
                QualityType.INSTALLED if repair_config.quality else QualityType.REQUIRED
            )
            self.repair_by_quality(units, quality_type)

        logger.info("repairing finished")
