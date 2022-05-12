from typing import Protocol
from autovirt.domain.shopboard import ShopBoard


class ShopGateway(Protocol):
    def get_shopboard(self, shop_id: int) -> ShopBoard:
        ...
