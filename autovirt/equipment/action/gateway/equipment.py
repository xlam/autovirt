from typing import Protocol, Optional

from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment


class EquipmentGateway(Protocol):
    def terminate(self, unit: UnitEquipment, quantity: int):
        ...

    def buy(self, unit: UnitEquipment, offer: RepairOffer, quantity: int):
        ...

    def get_offers(self, unit_id: int, quantity_from: int = 0) -> list[RepairOffer]:
        ...

    def get_offer_by_id(self, unit_id: int, offer_id: int) -> Optional[RepairOffer]:
        ...

    def repair(self, units: list[UnitEquipment], offer: RepairOffer):
        ...

    def get_units_to_repair(
        self,
        equipment_id: int,
        units_only: list[int] = None,
        units_exclude: list[int] = None,
    ) -> list[UnitEquipment]:
        ...
