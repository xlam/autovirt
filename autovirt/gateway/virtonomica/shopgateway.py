from autovirt.domain.shopboard import ShopBoard, ShopBoardItem

from typing import Protocol


class Adapter(Protocol):
    def fetch_shopboard(self, shop_id: int) -> list[dict]:
        ...


class ShopGateway:
    def __init__(self, adapter: Adapter):
        self._adapter = adapter

    def get_shopboard(self, shop_id: int) -> ShopBoard:
        items = self._adapter.fetch_shopboard(shop_id)
        res = []
        for item in items:
            res.append(
                ShopBoardItem(
                    unit_id=item["shop_unit_id"],
                    sales_volume=item["sales_volume"],
                    purchased_amount=item["purchased_amount"],
                    quantity=item["quantity"],
                    goods_category_id=item["goods_category_id"],
                )
            )
        return ShopBoard(res)
