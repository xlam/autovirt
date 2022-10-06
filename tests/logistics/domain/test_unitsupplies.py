import pytest

from autovirt.logistics.domain.unitsupplies import (
    UnitSupplies,
    SupplyContract,
    Supply,
)


@pytest.fixture
def contracts():
    return [
        SupplyContract(
            consumer_id=1, offer_id=1, supplier_id=1, free_for_buy=100, party_quantity=5
        ),
        SupplyContract(
            consumer_id=1, offer_id=2, supplier_id=2, free_for_buy=200, party_quantity=2
        ),
        SupplyContract(
            consumer_id=1, offer_id=3, supplier_id=3, free_for_buy=200, party_quantity=3
        ),
        SupplyContract(
            consumer_id=1, offer_id=4, supplier_id=4, free_for_buy=10, party_quantity=2
        ),
    ]


@pytest.fixture
def supplies_list(contracts):
    return [
        Supply(product_id=0, available=5, required=10, contracts=[contracts[0]]),
        Supply(product_id=1, available=10, required=5, contracts=[contracts[1:2]]),
        Supply(product_id=2, available=10, required=0, contracts=[contracts[3]]),
    ]


@pytest.fixture
def supplies(supplies_list):
    return UnitSupplies(supplies_list)


def test_get_supply_by_product_id(supplies):
    assert supplies.get_supply_by_product_id(product_id=0) == supplies[0]


def test_get_supply_by_product_id_throws_exception(supplies):
    index = len(supplies)
    with pytest.raises(IndexError):
        supplies.get_supply_by_product_id(product_id=index)


def test_get_contracts_by_product_id(supplies):
    assert supplies.get_contracts_by_product_id(product_id=2) == supplies[2].contracts


@pytest.mark.parametrize(
    "available, required, factor, expected",
    [
        (5, 10, 2, 20),
        (100, 10, 2, 0),
        (100, 0, 1, 0),
        (0, 0, 1, 0),
    ],
)
def test_set_ordered_product_quantity_by_stock_quantity_and_spent_factor(
    available, required, factor, expected, contracts
):
    supply = Supply(1, available, required, [contracts[1]])
    supply.set_order_by_required_factor(factor)
    assert supply.ordered == expected
