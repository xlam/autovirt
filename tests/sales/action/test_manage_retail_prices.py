from autovirt.sales.action.gateway.sales import SalesGateway
from autovirt.sales.action.manage_retail_prices import ManageRetailPricesAction
from autovirt.sales.domain import (
    Product,
    TwiceOfLocalPrice,
    ByShopsPriceAndQuality,
    ByMiddleValue,
)


class FakeSalesAdapter(SalesGateway):
    def __init__(self):
        self.updates: list[Product] = []

    def get_shop_products(self, shop_id) -> list[Product]:
        return [Product(1, "Product1", shop_id, 200000, 30, 50000, 2, 80000, 15)]

    def update_price_for(self, product):
        self.updates.append(product)


def test_manage_retail_prices():
    sales_adapter = FakeSalesAdapter()
    action = ManageRetailPricesAction(sales_adapter)

    result = action.run(shop_id=1, method=TwiceOfLocalPrice())
    assert len(result) > 0
    assert sales_adapter.updates[-1].price == 110000

    result = action.run(shop_id=1, method=ByShopsPriceAndQuality())
    assert len(result) > 0
    assert sales_adapter.updates[-1].price == 120000

    result = action.run(shop_id=1, method=ByMiddleValue())
    assert len(result) > 0
    assert sales_adapter.updates[-1].price == 100000
