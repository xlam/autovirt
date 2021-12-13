import pytest

from autovirt.domain.supply import Supply, SupplyItem, SupplyContract


@pytest.fixture
def supplies():
    return [
        SupplyItem(id=0, product_id=0, contracts=[]),
        SupplyItem(id=1, product_id=1, contracts=[]),
        SupplyItem(
            id=2,
            product_id=2,
            contracts=[SupplyContract(id=2, supplier_id=2)],
        ),
    ]


def test_get_supply_by_product_id(supplies):
    supply = Supply(supplies)
    assert supply.get_supply_by_product_id(product_id=0) == supplies[0]


def test_get_supply_by_product_id_exception(supplies):
    supply = Supply(supplies)
    with pytest.raises(RuntimeError):
        assert supply.get_supply_by_product_id(product_id=-1) == supplies[0]


def test_get_contracts_by_product_id(supplies):
    supply = Supply(supplies)
    assert supply.get_contracts_by_product_id(product_id=2) == supplies[2].contracts
