from pydantic import BaseModel


class SupplyContract(BaseModel):
    id: int
    supplier_id: int


class SupplyItem(BaseModel):
    id: int
    product_id: int
    contracts: list[SupplyContract]


class Supply(list):
    def __init__(self, items: list[SupplyItem] = None):
        items = items if items else []
        list.__init__(self, items)
        self._items = self

    def get_supply_by_product_id(self, product_id: int) -> SupplyItem:
        for item in self._items:
            if item.product_id == product_id:
                return item
        raise RuntimeError(f"Supply for {product_id=} is not found")

    def get_contracts_by_product_id(self, product_id: int) -> list[SupplyContract]:
        return self.get_supply_by_product_id(product_id).contracts
