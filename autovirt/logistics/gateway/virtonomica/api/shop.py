from autovirt.session import VirtSession


class ShopApiAdapter:
    def __init__(self, session: VirtSession):
        self.session = session

    def fetch_shopboard(self, shop_id: int) -> list[dict]:
        r = self.session.get(
            "https://virtonomica.ru/api/vera/main/unit/shopboard/browse",
            params={
                "id": shop_id,
            },
        )
        items = r.json().values()
        return items
