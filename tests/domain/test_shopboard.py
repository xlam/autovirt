import pytest

from autovirt.domain.shopboard import ShopBoard, ShopBoardItem

shopboard_data = [
    (0, 100, 100, 100, 123),
    (1, 150, 200, 350, 123),
    (2, 200, 2000, 10000, 123),
]


@pytest.fixture
def products():
    return [
        ShopBoardItem(
            unit_id=item[0],
            sales_volume=item[1],
            purchased_amount=item[2],
            quantity=item[3],
            goods_category_id=item[4],
        )
        for item in shopboard_data
    ]


def test_empty_shopboard_returns_no_excess_products():
    sb = ShopBoard()
    assert not sb.get_excess_products()


def test_init_with_products_list(products):
    sb = ShopBoard(products)
    assert len(sb) == 3


def test_get_excess_products(products):
    sb = ShopBoard(products)
    excess_products = sb.get_excess_products()
    assert products[1] in excess_products  # default multiplier=2
    assert products[2] in excess_products  # default multiplier=2
    assert sb.get_excess_products(multiplier=3) == [products[2]]
