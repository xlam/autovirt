from autovirt.sales import domain


def test_calculation_by_mid_values():
    product = domain.Product(1, "Product1", 1, 0, 31, 225234, 1.0, 222800, 3.0)
    price = domain.by_mid_values(product)
    assert price < product.locals_price * 2.5
