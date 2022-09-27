import pytest

from autovirt.logistics.domain.storageitem import StorageItem


@pytest.mark.parametrize(
    "quantity, spent, ordered, factor, expected",
    [
        (5, 10, 5, 2, 20),
        (100, 10, 30, 2, 0),
        (100, 0, 30, 1, 0),
        (0, 0, 0, 1, 0),
    ],
)
def test_set_ordered_product_quantity_by_stock_quantity_and_spent_factor(
    quantity, spent, ordered, factor, expected
):
    product = StorageItem(1, quantity, spent, ordered)
    product.set_order_by_spent_factor(factor)
    assert product.ordered == expected
