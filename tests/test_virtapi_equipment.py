import json
from unittest.mock import patch
from autovirt.virtapi import equipment
from autovirt.structs import UnitEquipment

with open("tests/repair-1529-json-short.txt", "r") as f:
    offers_data = json.load(f)
equipment_id = 1529
zero_weared_unit = 9113441
options = equipment.EquipmentGatewayOptions(company_id=0)


@patch("autovirt.virtapi.equipment.VirtSession")
@patch("autovirt.virtapi.equipment.Equipment._fetch_units")
def test_get_units_returns_valid_list(mock_fetch_units, mock_session):
    mock_fetch_units.return_value = offers_data
    e = equipment.Equipment(mock_session, options)
    units = e.get_units(equipment_id)
    assert type(units) == list
    assert type(units[0]) == UnitEquipment
    mock_fetch_units.assert_called_with(equipment_id)


@patch("autovirt.virtapi.equipment.VirtSession")
@patch("autovirt.virtapi.equipment.Equipment._fetch_units")
def test_get_units_filters_zero_weared(mock_fetch_units, mock_session):
    mock_fetch_units.return_value = offers_data
    e = equipment.Equipment(mock_session, options)
    units = e.get_units(equipment_id)
    ids = [unit.id for unit in units]
    assert zero_weared_unit not in ids
