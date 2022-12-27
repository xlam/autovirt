from typing import Protocol

from autovirt.logistics.domain.unit_supplies import UnitSupplies


class SuppliesGateway(Protocol):
    def get(self, unit_id: int) -> UnitSupplies:
        ...

    def set_supplies(self, supplies: UnitSupplies):
        ...
