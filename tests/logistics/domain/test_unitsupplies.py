import pytest

from autovirt.logistics.domain.supplies.unit_supplies import (
    SupplyNotFound,
    UnitSupplies,
)
from autovirt.logistics.domain.supplies.supply import Supply
from autovirt.logistics.domain.supplies.contract import Contract


@pytest.fixture
def contracts():
    return [
        Contract(
            consumer_id=1, offer_id=1, supplier_id=1, free_for_buy=100, party_quantity=5
        ),
        Contract(
            consumer_id=1, offer_id=2, supplier_id=2, free_for_buy=200, party_quantity=2
        ),
        Contract(
            consumer_id=1, offer_id=3, supplier_id=3, free_for_buy=200, party_quantity=3
        ),
        Contract(
            consumer_id=1, offer_id=4, supplier_id=4, free_for_buy=10, party_quantity=2
        ),
        Contract(
            consumer_id=1, offer_id=5, supplier_id=5, free_for_buy=0, party_quantity=5
        ),
    ]


@pytest.fixture
def supplies_list(contracts):
    return [
        Supply(
            unit_id=1,
            product_id=0,
            product_name="Product0",
            quantity=5,
            required=10,
            contracts=[contracts[0]],
        ),
        Supply(
            unit_id=1,
            product_id=1,
            product_name="Product1",
            quantity=10,
            required=5,
            contracts=[contracts[1:2]],
        ),
        Supply(
            unit_id=1,
            product_id=2,
            product_name="Product2",
            quantity=10,
            required=0,
            contracts=[contracts[3]],
        ),
    ]


@pytest.fixture
def supplies(supplies_list):
    return UnitSupplies(1, supplies_list)


def test_get_supply_by_product_id(supplies, supplies_list):
    assert supplies.get_supply_by_product_id(product_id=0) == supplies_list[0]


def test_get_supply_by_product_id_exception(supplies):
    index = len(supplies)
    with pytest.raises(SupplyNotFound):
        supplies.get_supply_by_product_id(product_id=index)


def test_get_contracts_by_product_id(supplies, supplies_list):
    assert (
        supplies.get_contracts_by_product_id(product_id=2) == supplies_list[2].contracts
    )


@pytest.mark.parametrize(
    "quantity, required, factor, expected",
    [
        (5, 10, 2, 20),
        (100, 10, 2, 0),
        (100, 0, 1, 0),
        (0, 0, 1, 0),
    ],
)
def test_set_ordered_product_quantity_by_stock_quantity_and_spent_factor(
    quantity, required, factor, expected, contracts
):
    supply = Supply(1, 1, "product1", quantity, required, [contracts[1]])
    supply.set_order_quantity_by_factor_of_required(factor)
    assert supply.ordered == expected


def test_no_free_for_buy_and_zero_required(contracts):
    s1 = Supply(1, 1, "product1", 5, 10, [contracts[4]])
    s1.set_order_quantity_by_factor_of_required(2)
    assert s1.ordered == 0
    s2 = Supply(1, 1, "product1", 5, 0, [contracts[1]])
    s2.set_order_quantity_by_factor_of_required(2)
    assert s2.ordered == 0
    s3 = Supply(1, 1, "product1", 0, 0, [contracts[1]])
    s3.set_order_quantity_by_factor_of_required(2)
    assert s3.ordered == 0


@pytest.mark.parametrize(
    "quantity, required, contracts, expected",
    [
        (100, 500, [Contract(1, 2, 3, 1000, 0)], 500),
        (600, 100, [Contract(1, 2, 3, 1000, 0)], 0),
        (0, 100, [Contract(1, 2, 3, 1000, 0)], 500),
        (
            0,
            100,
            [Contract(1, 1, 1, 1000, 0), Contract(1, 2, 2, 1000, 0)],
            500,
        ),
    ],
)
def test_set_order_quantity_by_target_share(quantity, required, contracts, expected):
    supply = Supply(1, 1, "product1", quantity, required, contracts)
    supply.set_order_quantity_by_target_quantity(target_quantity=500)
    assert supply.ordered == expected


def test_unit_supplies_checks_supply_for_valid_unit_id():
    us = UnitSupplies(1)
    us.append(Supply(2, 1, "product", 100, 100, []))
    assert len(us) == 0
