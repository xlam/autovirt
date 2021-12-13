from autovirt.session import get_logged_session as s


class ShopApi:
    def __init__(self):
        self._session = s()

    def fetch_shopboard(self, shop_id: int) -> list[dict]:
        r = self._session.get(
            "https://virtonomica.ru/api/vera/main/unit/shopboard/browse",
            params={
                "id": shop_id,
            },
        )
        items = r.json().values()
        return items
