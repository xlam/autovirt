from unittest.mock import Mock

import pytest

from autovirt.logistics.domain import StorageItem
from autovirt.logistics.action import OptimizeSuppliesAction
from autovirt.logistics.action.gateway import StorageGateway


@pytest.fixture
def storage():
    return [
        StorageItem(id=1, available=100, spent=5, ordered=10),
        StorageItem(2, 5, 10, 10),
        StorageItem(3, 200, 100, 200),
        StorageItem(4, 200, 10, 0),
    ]


@pytest.fixture
def mock_storage_gateway(storage):
    mock = Mock(spec=StorageGateway)
    mock.get.return_value = storage
    return mock


def test_optimize_supplies_action(mock_storage_gateway, storage):
    unit_id = 1
    factor = 2
    action = OptimizeSuppliesAction(mock_storage_gateway)
    res = action.execute(unit_id, factor)
    mock_storage_gateway.get.assert_called_with(unit_id)
    mock_storage_gateway.set_supplies.assert_called_with(storage[:2])
    assert res[0].ordered == 0
    assert res[1].ordered == 20
