import json

from autovirt.logistics.adapter.api_units import ApiUnitsGateway
from autovirt.gateway_options import GatewayOptions


class Response:
    @staticmethod
    def json():
        with open("tests/data/units-shops.json") as f:
            return json.load(f)


class FakeSession:
    @staticmethod
    def get(*args, **kwargs) -> Response:
        return Response()


def test_returns_correct_units_ids():
    units_gateway = ApiUnitsGateway(FakeSession(), GatewayOptions(company_id=0))  # type: ignore
    shops_ids = units_gateway.get_shops_ids()
    assert len(shops_ids) == 3
    assert 11085002 in shops_ids
