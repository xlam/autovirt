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


class RepairInputDTO(BaseModel):
    equipment_id: int
    units_only: Optional[list[int]] = None
    units_exclude: Optional[list[int]] = None
    keep_quality: Optional[bool] = None
    dry_run: bool = False


class RepairInstrumentation:
    def __init__(self):
        self.logger = utils.get_logger()

    def no_units_to_repair(self, equipment_id):
        self.logger.info(f"Nothing to repair {equipment_id}, exiting")

    def quality_groups_prepared(self, groups):
        self.logger.info(
            f"Prepared {len(groups)} unit groups with qualities {list(groups.keys())}"
        )

    def no_offers_found(self, equipment_id):
        self.logger.warning(f"No offers found to repair equipment {equipment_id}")

    def ready_to_repair(self, units, units_mismatch, quantity, quality):
        self.logger.info(
            f"Repairing {quantity} pieces of quality {quality} "
            f"on {len(units)} units (mismatched units: {len(units_mismatch)})"
        )

    def repair_finished(self, total_cost):
        self.logger.info(f"Total repair cost: {total_cost:.0f}")


class RepairAction:
    def __init__(self, equipment_adapter: EquipmentGateway):
        self.equipment_adapter = equipment_adapter
        self.instrumentation = RepairInstrumentation()

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
            self.instrumentation.no_offers_found(units_normal[0].equipment_id)
            return 0.0
        repair_cost = quantity * offer.cost

        self.instrumentation.ready_to_repair(
            units_normal, units_mismatch, quantity, quality
        )
        if not dry_run:
            self.equipment_adapter.repair(units_normal, offer)
        return repair_cost

    def run(self, input_dto: RepairInputDTO):
        units = self.equipment_adapter.get_units_to_repair(
            equipment_id=input_dto.equipment_id,
            units_only=input_dto.units_only,
            units_exclude=input_dto.units_exclude,
        )

        if not units:
            self.instrumentation.no_units_to_repair(input_dto.equipment_id)
            return

        quality_type = (
            QualityType.INSTALLED if input_dto.keep_quality else QualityType.REQUIRED
        )
        quality_groups = split_by_quality(units, quality_type=quality_type)
        self.instrumentation.quality_groups_prepared(quality_groups)
        total_cost = 0.0
        for quality, units in quality_groups.items():
            repair_cost = self.repair_with_quality(units, quality, input_dto.dry_run)
            total_cost += repair_cost
        self.instrumentation.repair_finished(total_cost)
