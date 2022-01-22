from autovirt import utils
from autovirt.session import VirtSession
from autovirt.artefact.interface import ArtefactGateway

logger = utils.get_logger()


class VirtArtefactGateway(ArtefactGateway):
    def __init__(self, session: VirtSession):
        self.s = session

    def _fetch_unit_slots(self, unit_id) -> list[dict]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/artefact/slots",
            params={"id": unit_id},
        )
        return list(r.json().values())

    def _fetch_slot_artefacts(self, slot_id, unit_id) -> list[dict]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/artefact/browse",
            params={"id": unit_id, "slot_id": slot_id},
        )
        return list(r.json().values())

    def _fetch_artefacts(self, slots, unit_id) -> list[dict]:
        artefacts = []
        for slot in slots:
            slot_artefacts = self._fetch_slot_artefacts(slot["id"], unit_id)
            artefacts.extend(slot_artefacts)
        return artefacts

    def attach(self, name, unit_id):

        # get unit artefact slots
        slots = self._fetch_unit_slots(unit_id)

        # get all artefacts for all unit slots
        artefacts = self._fetch_artefacts(slots, unit_id)

        url = "https://virtonomica.ru/api/vera/main/unit/artefact/attach"

        for artefact in artefacts:
            if artefact["name"] == name:
                params = {
                    "id": unit_id,
                    "artefact_id": artefact["id"],
                    "token": self.s.token,
                }
                logger.info(f"renewing: ({unit_id}) {name}")
                r = self.s.post(url, params)
                logger.info(r)
                break
