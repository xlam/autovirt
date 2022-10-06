from unittest.mock import Mock

import pytest

from autovirt.logistics.action import OptimizeSuppliesAction
from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.unitsupplies import Supply, UnitSupplies, SupplyContract


@pytest.fixture
def supplies():
    return UnitSupplies(
        [
            Supply(
                product_id=1,
                available=100,
                required=5,
                contracts=[
                    SupplyContract(
                        consumer_id=1,
                        offer_id=1,
                        supplier_id=11,
                        free_for_buy=100,
                        party_quantity=10,
                    )
                ],
            ),
            Supply(2, 5, 10, [SupplyContract(1, 2, 12, 100, 10)]),
            Supply(3, 200, 100, [SupplyContract(1, 3, 13, 100, 200)]),
            Supply(4, 200, 10, [SupplyContract(1, 4, 14, 100, 0)]),
        ]
    )


@pytest.fixture
def mock_supplies_gateway(supplies):
    mock = Mock(spec=SuppliesGateway)
    mock.get.return_value = supplies
    return mock


def test_optimize_supplies_action(mock_supplies_gateway, supplies):
    unit_id = 1
    factor = 2
    action = OptimizeSuppliesAction(mock_supplies_gateway)
    res = action.execute(unit_id, factor)
    mock_supplies_gateway.get.assert_called_with(unit_id)
    mock_supplies_gateway.set_supplies.assert_called_with(UnitSupplies(supplies[:2]))
    assert res[0].ordered == 0
    assert res[1].ordered == 20
