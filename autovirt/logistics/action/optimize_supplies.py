from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.unitsupplies import Supply, UnitSupplies


class OptimizeSuppliesAction:
    def __init__(self, supplies_gateway: SuppliesGateway):
        self.supplies_gateway = supplies_gateway

    def execute(self, unit_id: int, factor: int = 1) -> UnitSupplies:
        supplies = self.supplies_gateway.get(unit_id)
        changed_supplies = UnitSupplies()
        for supply in supplies:
            ordered = supply.ordered
            supply.set_order_by_required_factor(factor)
            if ordered != supply.ordered:
                changed_supplies.append(supply)
        self.supplies_gateway.set_supplies(changed_supplies)
        return changed_supplies
