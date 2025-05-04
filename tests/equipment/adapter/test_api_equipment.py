import json
from unittest.mock import Mock

from autovirt.equipment.adapter.api_equipment import ApiEquipmentAdapter
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment
from autovirt.gateway_options import GatewayOptions


class Response:
    def __init__(self, json_filename):
        self.filename = json_filename

    def json(self):
        with open(self.filename, "r") as f:
            return json.load(f)


def gateway_options():
    return GatewayOptions(company_id=0)


def test_get_units_returns_valid_all_list():
    equipment_id = 1528
    zero_weared_unit = 8821199
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/units-to-repair-1528.json"))
    units = adapter.get_units_to_repair(equipment_id)
    assert len(units) == 3
    assert isinstance(units[0], UnitEquipment)
    ids = [unit.id for unit in units]
    assert zero_weared_unit not in ids


def test_get_units_returns_only_specified_units():
    equipment_id = 1528
    specified_units_ids = [8821200]
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/units-to-repair-1528.json"))
    units = adapter.get_units_to_repair(equipment_id, units_only=specified_units_ids)
    assert len(units) == len(specified_units_ids)
    ids = [unit.id for unit in units]
    assert ids.sort() == specified_units_ids.sort()


def test_get_units_returns_all_but_specified_units():
    equipment_id = 1528
    specified_units_ids = [8821200]
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/units-to-repair-1528.json"))
    units = adapter.get_units_to_repair(equipment_id, units_exclude=specified_units_ids)
    ids = [unit.id for unit in units]
    assert len(units) == 2
    for unit_id in specified_units_ids:
        assert unit_id not in ids


def test_get_units_returns_empty_list_on_empty_json():
    equipment_id = 1528
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/units-to-repair-empty.json"))
    units = adapter.get_units_to_repair(equipment_id)
    assert len(units) == 0


def test_get_offers_returns_valid_list():
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/unit-offers.json"))
    offers = adapter.get_offers(unit_id=1)
    assert len(offers) > 0
    assert isinstance(offers[0], RepairOffer)


def test_get_offers_empty_json_returns_empty_list():
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/unit-offers-empty.json"))
    offers = adapter.get_offers(unit_id=1)
    assert len(offers) == 0


def test_get_offer_by_id_returns_valid_offer_or_none():
    adapter = ApiEquipmentAdapter(Mock(), gateway_options())
    adapter.s.get = Mock(return_value=Response("tests/data/unit-offers.json"))

    offer = adapter.get_offer_by_id(unit_id=1, offer_id=10177670)
    assert isinstance(offer, RepairOffer)
    assert offer.company_id == 5849249

    # not exists in test data
    offer = adapter.get_offer_by_id(unit_id=1, offer_id=777)
    assert offer is None
