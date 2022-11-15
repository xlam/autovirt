from dataclasses import dataclass

EXPIRE_THRESHOLD = 5


@dataclass
class Artefact:
    id: int
    name: str
    expires: int
    unit_id: int
    unit_name: str
    city_name: str


def filter_artefacts_to_renew(artefacts: list[Artefact]) -> list[Artefact]:
    res = []
    for artefact in artefacts:
        if artefact.expires < EXPIRE_THRESHOLD:
            res.append(artefact)
    return res
