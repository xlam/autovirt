import json
from unittest.mock import Mock

from autovirt.structs import UnitEquipment
from autovirt.virtapi import GatewayOptions
from autovirt.virtapi.equipment import VirtEquipment

with open("tests/data/repair-1529-json-short.txt", "r") as f:
    offers_data = json.load(f)
equipment_id = 1529
zero_weared_unit = 9113441
options = GatewayOptions(company_id=0)


def test_get_units_returns_valid_list():
    e = VirtEquipment(Mock(), options)
    e._fetch_units = Mock(return_value=offers_data)
    units = e.get_units_to_repair(equipment_id)
    assert isinstance(units[0], UnitEquipment)
    ids = [unit.id for unit in units]
    assert zero_weared_unit not in ids
