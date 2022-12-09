import abc

from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment


class EquipmentGateway(abc.ABC):
    @abc.abstractmethod
    def terminate(self, unit: UnitEquipment, quantity: int):
        pass

    @abc.abstractmethod
    def buy(self, unit: UnitEquipment, offer: RepairOffer, quantity: int):
        pass

    @abc.abstractmethod
    def get_offers(self, product_id: int) -> list[RepairOffer]:
        pass

    @abc.abstractmethod
    def repair(self, units: list[UnitEquipment], offer: RepairOffer):
        pass

    @abc.abstractmethod
    def get_units_to_repair(self, equipment_id: int) -> list[UnitEquipment]:
        pass
