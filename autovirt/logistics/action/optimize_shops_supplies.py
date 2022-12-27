from autovirt.logistics.action import OptimizeUnitSuppliesAction
from autovirt.logistics.action.gateway import UnitsGateway, SuppliesGateway
from autovirt.logistics.domain.unit_supplies import UnitSupplies


class OptimizeShopsSuppliesAction:
    def __init__(self, units_gateway: UnitsGateway, supplies_gateway: SuppliesGateway):
        self.units_gateway = units_gateway
        self.supplies_gateway = supplies_gateway

    def execute(self, factor: int = 1, dry_run: bool = False) -> list[UnitSupplies]:
        shops_ids = self.units_gateway.get_shops_ids()
        optimize_action = OptimizeUnitSuppliesAction(self.supplies_gateway)
        changed_supplies = []
        for shop_id in shops_ids:
            changed_supplies.append(optimize_action.execute(shop_id, factor, dry_run))
        return changed_supplies
