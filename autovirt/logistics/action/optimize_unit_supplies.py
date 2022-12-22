from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.unitsupplies import UnitSupplies, Supply
from autovirt.utils import get_logger


class OptimizeUnitSuppliesInstrumentation:
    def __init__(self):
        self.logger = get_logger()

    def setting_supplies(self, supply: Supply, old_ordered: int):
        for contract in supply.contracts:
            self.logger.info(
                f"Updating ordered quantity of '{supply.product_name}' {supply.product_id} "
                f"from {old_ordered} to {supply.ordered} at unit {supply.contracts[0].consumer_id}:"
            )
            self.logger.info(
                f"Ordering {contract.party_quantity} pieces from offer {contract.offer_id}"
            )


class OptimizeUnitSuppliesAction:
    def __init__(self, supplies_gateway: SuppliesGateway):
        self.supplies_gateway = supplies_gateway
        self.instrumentation = OptimizeUnitSuppliesInstrumentation()

    def execute(
        self, unit_id: int, factor: int = 1, dry_run: bool = False
    ) -> UnitSupplies:
        supplies = self.supplies_gateway.get(unit_id)
        changed_supplies = UnitSupplies()
        for supply in supplies:
            ordered = supply.ordered
            supply.set_order_quantity_by_factor_of_required(factor)
            if ordered != supply.ordered:
                changed_supplies.append(supply)
                self.instrumentation.setting_supplies(supply, old_ordered=ordered)
        if not dry_run:
            self.supplies_gateway.set_supplies(changed_supplies)
        return changed_supplies
