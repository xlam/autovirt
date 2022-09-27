from autovirt.logistics.domain import StorageItem
from autovirt.logistics.action.gateway import StorageGateway


class OptimizeSuppliesAction:
    def __init__(self, storage_gateway: StorageGateway):
        self.storage_gateway = storage_gateway

    def execute(self, unit_id: int, factor: int = 1) -> list[StorageItem]:
        storage = self.storage_gateway.get(unit_id)
        changed_storage = []
        for item in storage:
            ordered = item.ordered
            item.set_order_by_spent_factor(factor)
            if ordered != item.ordered:
                changed_storage.append(item)
        self.storage_gateway.set_supplies(changed_storage)
        return changed_storage
