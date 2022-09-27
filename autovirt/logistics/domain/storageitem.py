from dataclasses import dataclass


@dataclass
class StorageItem:
    id: int
    available: int
    spent: int
    ordered: int

    def set_order_by_spent_factor(self, factor: int = 1):
        if self.available > self.spent * factor:
            self.ordered = 0
        else:
            self.ordered = self.spent * factor
