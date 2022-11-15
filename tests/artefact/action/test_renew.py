from autovirt.artefact.action import RenewAction
from autovirt.artefact.action.gateway import ArtefactGateway
from autovirt.artefact.domain import Artefact, filter_artefacts_to_renew


class FakeArtefactGateway(ArtefactGateway):
    def __init__(self):
        self.artefacts: dict[int, Artefact] = {
            1: Artefact(1, "name1", 10, 1, "unit1", "city1"),
            2: Artefact(2, "name1", 3, 2, "unit1", "city1"),
            3: Artefact(3, "name1", 1, 3, "unit1", "city1"),
        }

    def get_artefacts(self) -> list[Artefact]:
        return list(self.artefacts.values())

    def attach(self, artefact: Artefact):
        if artefact.id not in self.artefacts.keys():
            self.artefacts[artefact.id] = artefact
        self.artefacts[artefact.id].expires = 15

    def remove(self, artefact: Artefact):
        del self.artefacts[artefact.id]


def test_renew():
    gw = FakeArtefactGateway()
    action = RenewAction(gw)
    action.run()
    artefacts = gw.get_artefacts()
    assert len(filter_artefacts_to_renew(artefacts)) == 0
