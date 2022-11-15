from typing import Protocol

from autovirt.artefact.domain import Artefact


class ArtefactGateway(Protocol):
    def get_artefacts(self) -> list[Artefact]:
        ...

    def attach(self, artefact: Artefact):
        ...

    def remove(self, artefact: Artefact):
        ...
