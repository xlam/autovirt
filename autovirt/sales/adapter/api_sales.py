from autovirt.sales.action.gateway.sales import SalesGateway
from autovirt.sales.domain import Product
from autovirt.session import VirtSession
from autovirt.utils import get_logger

logger = get_logger()


class ApiSalesAdapter(SalesGateway):
    def __init__(self, session: VirtSession):
        self.s = session

    def get_shop_products(self, shop_id) -> list[Product]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/shopboard/browse",
            params={"id": shop_id},
        )
        shopboard_products = r.json()
        retail_reports_by_category = {}
        for p in shopboard_products:
            if p["goods_category_id"] not in retail_reports_by_category:
                r = self.s.get(
                    "https://virtonomica.ru/api/vera/main/marketing/report/retail/byshop",
                    params={
                        "unit_id": p["shop_unit_id"],
                        "category_id": p["goods_category_id"],
                    },
                )
                retail_reports_by_category[p["goods_category_id"]] = r.json()
        products: list[Product] = []
        for p in shopboard_products:
            try:
                products.append(
                    Product(
                        int(p["product_id"]),
                        p["product_name"],
                        int(p["shop_unit_id"]),
                        float(p["price"]),
                        float(p["quality"]),
                        float(
                            retail_reports_by_category[p["goods_category_id"]][
                                p["product_id"]
                            ]["local_price"]
                        ),
                        float(
                            retail_reports_by_category[p["goods_category_id"]][
                                p["product_id"]
                            ]["local_quality"]
                        ),
                        float(p["city_middle_price"]),
                        float(p["city_middle_quality"]),
                    )
                )
            except KeyError as e:
                logger.error(f"Data key not found: {e}", exc_info=e)
                continue

        return products

    def update_price_for(self, product: Product):
        r = self.s.post(
            "https://virtonomica.ru/api/vera/main/unit/shopboard/set",
            params={
                "id": product.shop_id,
                "price": product.price,
                "product_id": product.id,
            },
        )
