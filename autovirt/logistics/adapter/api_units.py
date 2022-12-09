from autovirt.logistics.action.gateway import UnitsGateway
from autovirt.session import VirtSession
from autovirt.gateway_options import GatewayOptions


class ApiUnitsGateway(UnitsGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def get_shops_ids(self) -> list[int]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/units",
            params={"id": self.options.company_id, "unit_class_id": 1885},
        )
        ids = []
        for unit in list(r.json()["data"].values()):
            ids.append(int(unit["id"]))
        return ids
