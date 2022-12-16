from typing import Optional

from pydantic import BaseModel

from autovirt import utils
from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.domain.equipment import quantity_to_repair

logger = utils.get_logger()


class RepairWithOfferInputDTO(BaseModel):
    equipment_id: int
    units_only: Optional[list[int]] = None
    units_exclude: Optional[list[int]] = None
    offer_id: int
    dry_run: bool = False


class RepairWithOfferInstrumentation:
    def __init__(self):
        self.logger = utils.get_logger()

    def no_units_to_repair(self):
        self.logger.info("Nothing to repair, exiting")

    def offer_not_found(self, offer_id, equipment_id):
        self.logger.info(
            f"Offer {offer_id} for equipment {equipment_id} not found, exiting"
        )

    def ready_to_repair(self, units, offer):
        quantity = quantity_to_repair(units)
        total_cost = quantity * offer.cost
        self.logger.info(f"Repairing {quantity} pieces on {len(units)} units")
        self.logger.info(
            f"Using offer {offer.id} with quality {offer.quality} "
            f"and price {offer.cost} (repair cost: {total_cost:.0f})"
        )


class RepairWithOfferAction:
    def __init__(self, equipment_adapter: EquipmentGateway):
        self.equipment_adapter = equipment_adapter
        self.instrumentation = RepairWithOfferInstrumentation()

    def run(self, input_dto: RepairWithOfferInputDTO):
        units = self.equipment_adapter.get_units_to_repair(
            equipment_id=input_dto.equipment_id,
            units_only=input_dto.units_only,
            units_exclude=input_dto.units_exclude,
        )
        if not units:
            self.instrumentation.no_units_to_repair()
            return

        offer = self.equipment_adapter.get_offer_by_id(units[0].id, input_dto.offer_id)
        if not offer:
            self.instrumentation.offer_not_found(
                input_dto.offer_id, input_dto.equipment_id
            )
            return

        self.instrumentation.ready_to_repair(units, offer)
        if not input_dto.dry_run:
            self.equipment_adapter.repair(units, offer)
