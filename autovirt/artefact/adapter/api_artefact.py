from autovirt.artefact.action.gateway import ArtefactGateway
from autovirt.artefact.domain import Artefact
from autovirt.session import VirtSession
from autovirt.gateway_options import GatewayOptions
from autovirt import utils

logger = utils.get_logger()


class ApiArtefactAdapter(ArtefactGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def fetch_artefacts_data(self) -> list:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/artefact/units",
            params={"id": self.options.company_id, "pagesize": self.options.pagesize},
        )
        return list(r.json()["data"].values())

    def get_artefacts(self) -> list[Artefact]:
        artefacts_data = self.fetch_artefacts_data()
        res = []
        for unit in artefacts_data:
            for artefact in unit["artefacts"]["attached"].values():
                if artefact:
                    res.append(
                        Artefact(
                            int(artefact["id"]),
                            artefact["name"],
                            int(artefact["expires"]),
                            int(unit["id"]),
                            unit["name"],
                            unit["city_name"],
                        )
                    )
        return res

    def remove(self, artefact: Artefact):
        url = "https://virtonomica.ru/api/vera/main/unit/artefact/remove"
        params = {
            "id": artefact.unit_id,
            "artefact_id": artefact.id,
            "token": self.s.token,
        }
        r = self.s.post(url, params)
        logger.info(f"Remove response: {r.status_code} ({r.text})")

    def attach(self, artefact: Artefact):
        url = "https://virtonomica.ru/api/vera/main/unit/artefact/attach"
        params = {
            "id": artefact.unit_id,
            "artefact_id": artefact.id,
            "token": self.s.token,
        }
        r = self.s.post(url, params)
        logger.info(f"Attach response: {r.status_code} ({r.text})")
