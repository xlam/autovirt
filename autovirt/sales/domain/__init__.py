from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    shop_id: int
    price: float
    quality: float
    locals_price: float
    locals_quality: float
    shops_price: float
    shops_quality: float


def twice_of_local_price(product: Product) -> int:
    return int((product.locals_price + product.locals_price * 0.1) * 2)


def by_shops_price_and_quality(product: Product) -> int:
    quality_coeff = product.quality / product.shops_quality
    if quality_coeff > 1:
        return int(product.shops_price + product.shops_price / quality_coeff)
    elif quality_coeff < 1:
        return int(product.shops_price - product.shops_price * quality_coeff)
    else:
        return int(product.shops_price * 0.9)


def by_complex_factors(product: Product) -> int:
    min_quality = min(product.locals_quality, product.shops_quality)
    min_price = min(product.locals_price, product.shops_price)
    quality_coeff = product.quality / min_quality
    if quality_coeff > 1:
        return int(min_price + min_price / quality_coeff)
    elif quality_coeff < 1:
        return int(min_price - min_price * quality_coeff)
    else:
        return int(min_price * 0.9)


def by_mid_values(product: Product) -> int:
    mid_quality = (product.locals_quality + product.shops_quality) / 2
    mid_price = (product.locals_price + product.shops_price) / 2
    quality_coeff = product.quality / mid_quality
    if quality_coeff > 1:
        price = int(mid_price + mid_price * (quality_coeff - 1))
        return min(price, int(product.locals_price * 2))
    elif quality_coeff < 1:
        return int(mid_price - mid_price * (1 - quality_coeff))
    else:
        return int(mid_price * 0.9)
