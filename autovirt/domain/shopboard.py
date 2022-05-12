from __future__ import annotations
from pydantic import BaseModel


class ShopBoardItem(BaseModel):
    unit_id: int
    sales_volume: int
    purchased_amount: int
    quantity: int
    goods_category_id: int


class ShopBoard(list):
    def __init__(self, items: list[ShopBoardItem] = None):
        items = items if items else []
        list.__init__(self, items)

    def get_excess_products(self, multiplier: int = 2) -> ShopBoard:
        res = []
        for item in self:
            if item.quantity / item.sales_volume > multiplier:
                res.append(item)
        return ShopBoard(res)
