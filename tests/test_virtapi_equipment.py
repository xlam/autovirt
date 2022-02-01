import json
from unittest.mock import patch, Mock

import pytest

from autovirt.session import VirtSession
from autovirt.structs import UnitEquipment
from autovirt.virtapi import equipment, GatewayOptions

with open("tests/data/repair-1529-json-short.txt", "r") as f:
    offers_data = json.load(f)
equipment_id = 1529
zero_weared_unit = 9113441
options = GatewayOptions(company_id=0)


@pytest.fixture
def mock_session():
    mock = Mock(spec=VirtSession)
    return mock


@patch("autovirt.virtapi.equipment.VirtEquipment._fetch_units")
def test_get_units_returns_valid_list(mock_fetch_units, mock_session):
    mock_fetch_units.return_value = offers_data
    e = equipment.VirtEquipment(mock_session, options)
    units = e.get_units_to_repair(equipment_id)
    assert type(units[0]) == UnitEquipment
    ids = [unit.id for unit in units]
    assert zero_weared_unit not in ids
