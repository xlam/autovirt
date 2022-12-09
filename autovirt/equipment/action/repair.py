import sys
from typing import Optional

from pydantic import BaseModel

from autovirt import utils
from autovirt.equipment.domain.equipment import (
    QualityType,
    quantity_to_repair,
    filter_offers,
    select_offer,
    select_offer_to_raise_quality,
    split_by_quality,
    split_mismatch_quality_units,
)
from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.domain.unit_equipment import UnitEquipment

logger = utils.get_logger()


class RepairInputDTO(BaseModel):
    equipment_id: int
    include: Optional[list[int]] = None
    exclude: Optional[list[int]] = None
    offer_id: Optional[int] = None
    keep_quality: Optional[bool] = None
    dry_run: bool = False


class RepairAction:
    def __init__(self, equipment_adapter: EquipmentGateway):
        self.equipment_adapter = equipment_adapter

    def fix_units_quality(
        self, units: list[UnitEquipment], margin: float = 0, dry_run: bool = False
    ):
        for unit in units:
            # need to update offers before each operation
            offers = self.equipment_adapter.get_offers(unit.id)
            res = select_offer_to_raise_quality(unit, offers, margin)
            if not res:
                logger.info(
                    f"no offers found to fix unit {unit.id} "
                    f"(installed quality: {unit.quality_installed}, required: {unit.quality_required}), skipping"
                )
                continue
            (offer, quantity) = res
            logger.info(
                f"got offer {offer.id} (quality: {offer.quality}, price: {offer.price}) "
                f"to replace {quantity} items at unit {unit.id} "
                f"(installed quality: {unit.quality_installed}, required: {unit.quality_required})"
            )
            if not dry_run:
                self.equipment_adapter.terminate(unit, quantity)
                self.equipment_adapter.buy(unit, offer, quantity)

    def repair_with_quality(
        self, units: list[UnitEquipment], quality: float, dry_run: bool = False
    ) -> float:
        units_normal, units_mismatch = split_mismatch_quality_units(units)
        if units_mismatch:
            logger.info("mismatch units qualities found, fixing them:")
            logger.info(units_mismatch)
            self.fix_units_quality(units_mismatch, dry_run=dry_run)
        if not units_normal:
            logger.info("nothing to repair, exiting")
            sys.exit(0)
        quantity = quantity_to_repair(units_normal)
        offers = self.equipment_adapter.get_offers(units_normal[0].id, quantity)
        offers = filter_offers(offers, quality, quantity)
        offer = select_offer(offers, units_normal, quality)
        if not offer:
            logger.error(
                f"could not select offer to repair quality {quality}, skipping"
            )
            return 0.0
        repair_cost = quantity * offer.price
        logger.info(
            f"found offer {offer.id} with quality {offer.quality} "
            f"and price {offer.price} (repair cost: {repair_cost:.0f})"
        )
        logger.info(
            f"repairing {quantity} pieces of quality {quality} on {len(units)} units"
        )
        if not dry_run:
            self.equipment_adapter.repair(units_normal, offer)
        return repair_cost

    @staticmethod
    def filter_units_with_exclude_and_include_options(
        units: list[UnitEquipment], repair_options: RepairInputDTO
    ) -> list[UnitEquipment]:
        if repair_options.exclude:
            excludes = repair_options.exclude
            units = [unit for unit in units for ex in excludes if unit.id != ex]
        if repair_options.include:
            includes = repair_options.include
            units = [unit for unit in units for inc in includes if unit.id == inc]
        return units

    def repair_by_quality(
        self,
        units: list[UnitEquipment],
        quality_type: QualityType,
        dry_run: bool = False,
    ):
        units_ = split_by_quality(units, quality_type=quality_type)
        logger.info(
            f"prepared units with {len(units_)} quality levels: {list(units_.keys())}"
        )
        total_cost = 0.0
        for quality, units_list in units_.items():
            repair_cost = self.repair_with_quality(units_list, quality, dry_run)
            total_cost += repair_cost
        logger.info(f"total repair cost: {total_cost:.0f}")

    def repair_with_offer(
        self, units: list[UnitEquipment], offer_id: int, dry_run: bool = False
    ) -> float:
        quantity = quantity_to_repair(units)
        offers = self.equipment_adapter.get_offers(units[0].id, quantity)
        offer = [o for o in offers if o.id == offer_id][0]
        total_cost = quantity * offer.price
        logger.info(f"repairing {quantity} pieces on {len(units)} units")
        logger.info(
            f"using offer {offer.id} with quality {offer.quality} "
            f"and price {offer.price} (repair cost: {total_cost:.0f})"
        )
        if not dry_run:
            self.equipment_adapter.repair(units, offer)
        return total_cost

    def run(self, input_dto: RepairInputDTO):
        logger.info(f"starting repair equipment id {input_dto.equipment_id}")
        units = self.equipment_adapter.get_units_to_repair(input_dto.equipment_id)
        units = self.filter_units_with_exclude_and_include_options(units, input_dto)

        if not units:
            logger.info("nothing to repair, exiting")
            return

        if input_dto.offer_id:
            self.repair_with_offer(units, input_dto.offer_id, input_dto.dry_run)
        else:
            quality_type = (
                QualityType.INSTALLED
                if input_dto.keep_quality
                else QualityType.REQUIRED
            )
            self.repair_by_quality(units, quality_type, input_dto.dry_run)

        logger.info("repairing finished")
