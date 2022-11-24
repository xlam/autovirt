import json

from autovirt.sales.adapter.api_sales import ApiSalesAdapter
from autovirt.sales.domain import Product


class Response:
    def __init__(self, filename):
        with open(filename, "r") as file:
            self.data = json.load(file)

    def json(self):
        return self.data


class FakeSession:
    def __init__(self):
        self.get_count = 0

    def get(self, *args, **kwargs):
        self.get_count += 1
        if self.get_count == 1:
            return Response("tests/sales/data/shopboard.json")
        elif self.get_count == 2:
            return Response("tests/sales/data/report-byshop.json")


def test_returns_correct_products():
    session = FakeSession()
    adapter = ApiSalesAdapter(session)  # type: ignore
    products = adapter.get_shop_products(shop_id=11057258)

    product = Product(
        15335,
        "Спортинвентарь",
        11057258,
        80000.0,
        31.6418144798178,
        33556.72,
        3.9,
        57106.3525679459,
        15.48,
    )

    assert len(products) == 2
    assert product in products
