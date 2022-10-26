import json

from autovirt.logistics.adapter.supplies import ApiSuppliesGateway


class Response:
    @staticmethod
    def json():
        with open("tests/data/shop-supply-summary.json") as f:
            return json.load(f)


class FakeSession:
    @staticmethod
    def get(*args, **kwargs) -> Response:
        return Response()


def test_returns_correct_supplies():
    supplies_gateway = ApiSuppliesGateway(FakeSession())  # type: ignore
    # we don't need real unit id to test with FakeSession
    unit_supplies = supplies_gateway.get(unit_id=0)
    assert len(unit_supplies) == 3
    assert unit_supplies[0].product_id == 422201
    assert len(unit_supplies[0].contracts) == 1
