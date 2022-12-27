import abc

from autovirt.logistics.domain.unit_supplies import Supply, UnitSupplies


class SuppliesGateway(abc.ABC):
    @abc.abstractmethod
    def get(self, unit_id: int) -> UnitSupplies:
        pass

    @abc.abstractmethod
    def set_supplies(self, supplies: UnitSupplies):
        pass
