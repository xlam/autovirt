import json

from autovirt.logistics.adapter.api_shop import ApiShopGateway
from autovirt.logistics.domain.unit_product import UnitProduct
from autovirt.logistics.domain.warehouse import Warehouse


class Response:
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data


class FakeSession:
    def __init__(self, json_data: str):
        self.json_data = json_data

    def get(self, *args, **kwargs) -> Response:
        return Response(self.json_data)


def load_json_data(filename: str):
    with open(filename) as f:
        return json.load(f)


def test_returns_correct_unit_products():
    shop_gateway = ApiShopGateway(
        FakeSession(load_json_data("tests/logistics/data/shop_products.json"))  # type: ignore
    )
    products = shop_gateway.get_shop_products(unit_id=1)
    expected = UnitProduct(15334, "Бейсболка", 8408693, 1212714, 15000)
    assert len(products) == 6
    assert expected in products


def test_returns_correct_warehouses_for_product():
    shop_gateway = ApiShopGateway(
        FakeSession(load_json_data("tests/logistics/data/shop_warehouses.json"))  # type: ignore
    )
    product = UnitProduct(15334, "Бейсболка", 8408693, 1212714, 15000)
    warehouses = shop_gateway.get_warehouses_for(product)
    expected = Warehouse(10113313, 51277, 909.023516269994)
    assert len(warehouses) == 2
    assert expected in warehouses
