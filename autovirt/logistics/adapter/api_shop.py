from autovirt import utils

from autovirt.logistics.action.gateway.shop import ShopGateway
from autovirt.logistics.domain import Warehouse
from autovirt.logistics.domain.delivery import Delivery
from autovirt.logistics.domain.unit_product import UnitProduct
from autovirt.session import VirtSession


logger = utils.get_logger()


class ApiShopGateway(ShopGateway):
    def __init__(self, session: VirtSession):
        self.s = session

    def get_shop_products(self, unit_id: int) -> list[UnitProduct]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/shopboard/browse",
            params={"id": unit_id},
        )
        products = []
        for product in r.json():
            products.append(
                UnitProduct(
                    int(product["product_id"]),
                    product["product_name"],
                    int(product["shop_unit_id"]),
                    int(product["quantity"]),
                    int(product["order_amount"]),
                )
            )
        return products

    def get_warehouses_for(self, product: UnitProduct) -> list[Warehouse]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/storage/delivery/units",
            params={"id": product.unit_id, "product_id": product.id},
        )
        warehouses = []
        for warehouse in r.json()["data"].values():
            warehouses.append(
                Warehouse(
                    int(warehouse["id"]),
                    int(warehouse["qty"]),
                    float(warehouse["total_cost"]),
                )
            )
        return warehouses

    def set_delivery(self, delivery: Delivery):
        url = "https://virtonomica.ru/api/vera/main/unit/storage/delivery/set"
        params = {
            "id": delivery.from_unit_id,
            "unit_id": delivery.to_unit_id,
            "product_id": delivery.product_id,
            "qty": delivery.quantity,
            "token": self.s.token,
        }
        r = self.s.post(url, params)
        logger.info(f"response: {r}")
