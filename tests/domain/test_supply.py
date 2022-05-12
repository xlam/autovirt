import pytest

from autovirt.domain.supplies import Supplies, Supply, SupplyContract


@pytest.fixture
def supplies_list():
    return [
        Supply(id=0, product_id=0, contracts=[]),
        Supply(id=1, product_id=1, contracts=[]),
        Supply(
            id=2,
            product_id=2,
            contracts=[SupplyContract(id=2, supplier_id=2)],
        ),
    ]


@pytest.fixture
def supplies(supplies_list):
    return Supplies(supplies_list)


def test_get_supply_by_product_id(supplies):
    assert supplies.get_supply_by_product_id(product_id=0) == supplies[0]


def test_get_supply_by_product_id_exception(supplies):
    index = len(supplies)
    with pytest.raises(IndexError):
        supplies.get_supply_by_product_id(product_id=index)


def test_get_contracts_by_product_id(supplies):
    assert supplies.get_contracts_by_product_id(product_id=2) == supplies[2].contracts
