import abc

from autovirt.structs import UnitEquipment, RepairOffer


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
    def get_units(self, equipment_id: int) -> list[UnitEquipment]:
        pass
