from dataclasses import dataclass
from typing import Protocol


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


class RetailPriceCalculator(Protocol):
    def __call__(self, product: Product) -> float:
        ...


class TwiceOfLocalPrice(RetailPriceCalculator):
    def __call__(self, product: Product) -> float:
        return int((product.locals_price + product.locals_price * 0.1) * 2)


class ByShopsPriceAndQuality(RetailPriceCalculator):
    def __call__(self, product: Product) -> float:
        quality_coeff = product.quality / product.shops_quality
        if quality_coeff > 1:
            return int(product.shops_price + product.shops_price / quality_coeff)
        elif quality_coeff < 1:
            return int(product.shops_price - product.shops_price * quality_coeff)
        else:
            return int(product.shops_price * 0.9)


class ByComplexFactors(RetailPriceCalculator):
    def __call__(self, product: Product) -> float:
        min_quality = min(product.locals_quality, product.shops_quality)
        min_price = min(product.locals_price, product.shops_price)
        quality_coeff = product.quality / min_quality
        if quality_coeff > 1:
            return int(min_price + min_price / quality_coeff)
        elif quality_coeff < 1:
            return int(min_price - min_price * quality_coeff)
        else:
            return int(min_price * 0.9)


class ByMiddleValue(RetailPriceCalculator):
    def __call__(self, product: Product) -> float:
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


class ByLocalPrice(RetailPriceCalculator):
    def __call__(self, product: Product) -> float:
        return int(product.quality / product.locals_quality * product.locals_price)
