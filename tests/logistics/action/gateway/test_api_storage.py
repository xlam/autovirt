import json

from autovirt.virtapi.storage import ApiStorageGateway


class Response:
    @staticmethod
    def json():
        with open("tests/data/shop-supply-summary.json") as f:
            return json.load(f)


class FakeSession:
    @staticmethod
    def get(*args, **kwargs) -> Response:
        return Response()


def test_returns_correct_storage_items():
    storage = ApiStorageGateway(FakeSession())  # type: ignore
    # we don't need real unit id to test with FakeSession
    storage_items = storage.get(unit_id=0)
    assert len(storage_items) == 3
