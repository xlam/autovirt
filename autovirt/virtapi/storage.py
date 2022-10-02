from autovirt.session import VirtSession
from autovirt.logistics.domain import StorageItem
from autovirt.logistics.action.gateway import StorageGateway


class ApiStorageGateway(StorageGateway):
    def __init__(self, session: VirtSession):
        self.s = session

    def get(self, unit_id: int) -> list[StorageItem]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/supply/summary",
            params={"id": unit_id},
        )
        data = list(r.json().values())
        result = []
        for item in data:
            result.append(
                StorageItem(
                    int(item["product_id"]),
                    int(item["available"]),
                    int(item["required"]),
                    int(item["ordered"]),
                )
            )
        return result

    def set_supplies(self, storage: list[StorageItem]):
        pass
