import json
from unittest.mock import Mock

import pytest

from autovirt.artefact.adapter import ArtefactAdapter
from autovirt.artefact.domain import Artefact
from autovirt.session import VirtSession
from autovirt.virtapi import GatewayOptions


class Response:
    @staticmethod
    def json():
        with open("tests/data/artefacts.json", "r") as f:
            data = json.load(f)
        return data


@pytest.fixture
def session_mock():
    mock = Mock(spec_set=VirtSession)
    mock.token = 1
    return mock


@pytest.fixture
def artefact():
    return Artefact(
        302661,
        "Partnership agreement with an advertising agency",
        57,
        11085002,
        "Store ",
        "Puebla de Zaragoza",
    )


def test_returns_correct_artefacts(session_mock, artefact):
    session_mock.get.return_value = Response()
    adapter = ArtefactAdapter(session_mock, GatewayOptions(company_id=0))
    artefacts = adapter.get_artefacts()
    assert len(artefacts) == 5
    assert type(artefacts[0]) == Artefact
    assert artefacts[0] == artefact


def test_attach(session_mock, artefact):
    adapter = ArtefactAdapter(session_mock, GatewayOptions(company_id=0))
    adapter.attach(artefact)
    session_mock.post.assert_called_with(
        "https://virtonomica.ru/api/vera/main/unit/artefact/attach",
        {
            "id": artefact.unit_id,
            "artefact_id": artefact.id,
            "token": session_mock.token,
        },
    )


def test_remove(session_mock, artefact):
    adapter = ArtefactAdapter(session_mock, GatewayOptions(company_id=0))
    adapter.remove(artefact)
    session_mock.post.assert_called_with(
        "https://virtonomica.ru/api/vera/main/unit/artefact/remove",
        {
            "id": artefact.unit_id,
            "artefact_id": artefact.id,
            "token": session_mock.token,
        },
    )


def test_artefact_should_be_removed_before_renewal():
    pass
