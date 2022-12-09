import json
from unittest.mock import Mock

from autovirt.equipment.domain.unit_equipment import UnitEquipment
from autovirt.gateway_options import GatewayOptions
from autovirt.equipment.adapter.api_equipment import ApiEquipmentAdapter

with open("tests/data/repair-1529-json-short.txt", "r") as f:
    offers_data = json.load(f)
equipment_id = 1529
zero_weared_unit = 9113441
options = GatewayOptions(company_id=0)


def test_get_units_returns_valid_list():
    e = ApiEquipmentAdapter(Mock(), options)
    e._fetch_units = Mock(return_value=offers_data)
    units = e.get_units_to_repair(equipment_id)
    assert isinstance(units[0], UnitEquipment)
    ids = [unit.id for unit in units]
    assert zero_weared_unit not in ids
