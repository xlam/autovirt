import pytest
from unittest.mock import patch

from autovirt.virtapi.artefact import VirtArtefact


@pytest.fixture
def slots_data():
    return [
        {
            "id": "300138",
            "name": "Управление",
            "symbol": "management",
            "sort_order": "90",
            "enabled": "t",
        },
        {
            "id": "300136",
            "name": "Склад",
            "symbol": "warehouse",
            "sort_order": "80",
            "enabled": "t",
        },
        {
            "id": "300139",
            "name": "Производство",
            "symbol": "production",
            "sort_order": "70",
            "enabled": "t",
        },
        {
            "id": "300137",
            "name": "Прочее",
            "symbol": "other",
            "sort_order": "1",
            "enabled": "t",
        },
    ]


@pytest.fixture
def slot_artefacts_data():
    return {
        "300138": [
            {
                "id": "300893",
                "unit_id": "10402133",
                "artefact_id": "300893",
                "name": "ERP-система управления",
                "desc": "",
                "symbol": "20215672.gif",
                "initial_cost": "0",
                "point_cost": "3",
                "cost_per_turn": "0",
                "ttl": "365",
                "expires": "0",
            }
        ],
        "300136": [
            {
                "id": "302605",
                "unit_id": "10402133",
                "artefact_id": "302605",
                "name": "Система складской маркировки",
                "desc": "",
                "symbol": "145246100406.gif",
                "initial_cost": "100000",
                "point_cost": "0",
                "cost_per_turn": "50000",
                "ttl": "180",
                "expires": "0",
            }
        ],
        "300139": [
            {
                "id": "300875",
                "unit_id": "10402133",
                "artefact_id": "300875",
                "name": "Система контроля качества",
                "desc": "",
                "symbol": "20220936.png",
                "initial_cost": "0",
                "point_cost": "1",
                "cost_per_turn": "0",
                "ttl": "90",
                "expires": "0",
            },
            {
                "id": "300804",
                "unit_id": "10402133",
                "artefact_id": "300804",
                "name": "Солнечные батареи",
                "desc": "",
                "symbol": "20213666.gif",
                "initial_cost": "100000",
                "point_cost": "0",
                "cost_per_turn": "50000",
                "ttl": "365",
                "expires": "363",
            },
        ],
        "300137": [
            {
                "id": "300990",
                "unit_id": "10402133",
                "artefact_id": "300990",
                "name": "Продлённая гарантия",
                "desc": "",
                "symbol": "20285651.png",
                "initial_cost": "100000",
                "point_cost": "0",
                "cost_per_turn": "150000",
                "ttl": "365",
                "expires": "0",
            }
        ],
    }


@patch("autovirt.virtapi.artefact.VirtSession")
@patch("autovirt.virtapi.artefact.VirtArtefact._fetch_unit_slots")
@patch("autovirt.virtapi.artefact.VirtArtefact._fetch_slot_artefacts")
def test_attach(
    fetch_slot_artefacts_mock,
    fetch_unit_slots_mock,
    session_mock,
    slots_data,
    slot_artefacts_data,
):
    def fetch_unit_slot(slot_id_, unit_id):
        return slot_artefacts_data[slot_id_]

    fetch_unit_slots_mock.return_value = slots_data
    fetch_slot_artefacts_mock.side_effect = fetch_unit_slot
    session_mock.token = 1
    slot_id = "300137"
    artefact = VirtArtefact(session_mock)
    artefact.attach(
        slot_artefacts_data[slot_id][0]["name"],
        slot_artefacts_data[slot_id][0]["unit_id"],
    )
    session_mock.post.assert_called_with(
        "https://virtonomica.ru/api/vera/main/unit/artefact/attach",
        {
            "id": slot_artefacts_data[slot_id][0]["unit_id"],
            "artefact_id": slot_artefacts_data[slot_id][0]["id"],
            "token": session_mock.token,
        },
    )
