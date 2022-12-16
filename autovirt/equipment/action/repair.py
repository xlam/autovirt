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
    split_mismatch_required_quality_units,
)
from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.domain.unit_equipment import UnitEquipment

logger = utils.get_logger()


class RepairInputDTO(BaseModel):
    equipment_id: int
    units_only: Optional[list[int]] = None
    units_exclude: Optional[list[int]] = None
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
            offer, quantity = select_offer_to_raise_quality(unit, offers, margin)
            if not offer:
                continue
            if not dry_run:
                self.equipment_adapter.terminate(unit, quantity)  # type: ignore
                self.equipment_adapter.buy(unit, offer, quantity)  # type: ignore

    def repair_with_quality(
        self, units: list[UnitEquipment], quality: float, dry_run: bool = False
    ) -> float:
        units_normal, units_mismatch = split_mismatch_required_quality_units(units)
        if units_mismatch:
            self.fix_units_quality(units_mismatch, dry_run=dry_run)
        if not units_normal:
            sys.exit(0)
        quantity = quantity_to_repair(units_normal)
        offers = self.equipment_adapter.get_offers(units_normal[0].id, quantity)
        offers = filter_offers(offers, quality, quantity)
        offer = select_offer(offers, units_normal, quality)
        if not offer:
            return 0.0
        repair_cost = quantity * offer.cost
        logger.info(
            f"repairing {quantity} pieces of quality {quality} on {len(units)} units"
        )
        if not dry_run:
            self.equipment_adapter.repair(units_normal, offer)
        return repair_cost

    def repair_by_quality(
        self,
        units: list[UnitEquipment],
        quality_type: QualityType,
        dry_run: bool = False,
    ):
        quality_groups = split_by_quality(units, quality_type=quality_type)
        logger.info(
            f"prepared {len(quality_groups)} unit groups with qualities {list(quality_groups.keys())}"
        )
        total_cost = 0.0
        for quality, units in quality_groups.items():
            repair_cost = self.repair_with_quality(units, quality, dry_run)
            total_cost += repair_cost
        logger.info(f"total repair cost: {total_cost:.0f}")

    def run(self, input_dto: RepairInputDTO):
        logger.info(f"starting repair equipment id {input_dto.equipment_id}")
        units = self.equipment_adapter.get_units_to_repair(
            equipment_id=input_dto.equipment_id,
            units_only=input_dto.units_only,
            units_exclude=input_dto.units_exclude,
        )

        if not units:
            logger.info("nothing to repair, exiting")
            return

        quality_type = (
            QualityType.INSTALLED if input_dto.keep_quality else QualityType.REQUIRED
        )
        self.repair_by_quality(units, quality_type, input_dto.dry_run)

        logger.info("repairing finished")
