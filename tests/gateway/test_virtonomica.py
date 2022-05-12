from autovirt.gateway.virtonomica.shopgateway import ShopGateway


def data(shop_id: int) -> list[dict]:
    return [
        {
            "shop_unit_id": shop_id,
            "sales_volume": 100,
            "purchased_amount": 100,
            "quantity": 100,
            "goods_category_id": 0,
        },
        {
            "shop_unit_id": shop_id,
            "sales_volume": 100,
            "purchased_amount": 200,
            "quantity": 300,
            "goods_category_id": 0,
        },
        {
            "shop_unit_id": shop_id,
            "sales_volume": 100,
            "purchased_amount": 1000,
            "quantity": 10000,
            "goods_category_id": 0,
        },
    ]


class ShopApiMock:
    def __init__(self):
        self._shop_id = None

    def fetch_shopboard(self, shop_id: int) -> list[dict]:
        self._shop_id = shop_id
        return data(shop_id)


def test_shop_gateway():
    shop_id = 1
    gw = ShopGateway(ShopApiMock())
    res = gw.get_shopboard(shop_id)
    from autovirt.domain.shopboard import ShopBoard

    assert isinstance(res, ShopBoard)
    assert len(res) == len(data(shop_id))
    assert res[0].unit_id == shop_id
