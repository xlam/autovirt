from pydantic import BaseModel


class SupplyContract(BaseModel):
    id: int
    supplier_id: int


class Supply(BaseModel):
    id: int
    product_id: int
    contracts: list[SupplyContract]


class Supplies(list):
    def __init__(self, items: list[Supply] = None):
        items = items if items else []
        list.__init__(self, items)

    def get_supply_by_product_id(self, product_id: int) -> Supply:
        for item in self:
            if item.product_id == product_id:
                return item
        raise IndexError(f"Supply for product_id={product_id} is not found")

    def get_contracts_by_product_id(self, product_id: int) -> list[SupplyContract]:
        return self.get_supply_by_product_id(product_id).contracts
