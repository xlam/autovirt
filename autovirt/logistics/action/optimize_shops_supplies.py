from autovirt.logistics.action import OptimizeUnitSuppliesAction
from autovirt.logistics.action.gateway import SuppliesGateway, UnitsGateway
from autovirt.logistics.domain.supplies.unit_supplies import UnitSupplies


class OptimizeShopsSuppliesAction:
    def __init__(
        self,
        units_gateway: UnitsGateway,
        supplies_gateway: SuppliesGateway,
        dry_run: bool = False,
    ):
        self.units_gateway = units_gateway
        self.supplies_gateway = supplies_gateway
        self.dry_run = dry_run

    def execute(self, factor: int = 1) -> list[UnitSupplies]:
        shops_ids = self.units_gateway.get_shops_ids()
        optimize_action = OptimizeUnitSuppliesAction(self.supplies_gateway)
        changed_supplies = []
        for shop_id in shops_ids:
            changed_supplies.append(optimize_action.execute(shop_id, factor))
        return changed_supplies
