from unittest.mock import Mock

import pytest

from autovirt.equipment.domain.equipment import (
    QualityType,
    quantity_to_repair,
    quantity_total,
    select_offer,
    select_offer_to_raise_quality,
    split_by_quality,
    split_mismatch_quality_units,
    NoSiutableOffersExists,
)
from autovirt.equipment.interface import EquipmentGateway
from autovirt.equipment.repair import (
    RepairConfig,
    RepairAction,
)
from autovirt.structs import UnitEquipment, RepairOffer


@pytest.fixture
def options():
    return {"comp": {}}


@pytest.fixture
def units():
    return [
        UnitEquipment(1, 1000, 1000, 31, 30, 5, 1529),
        UnitEquipment(2, 2000, 2000, 32, 30, 20, 1529),
        UnitEquipment(3, 3000, 3000, 33, 30, 80, 1529),
    ]


@pytest.fixture
def units_mismatch():
    return [
        UnitEquipment(1, 1000, 1000, 29, 30, 5, 1529),
        UnitEquipment(2, 2000, 2000, 32, 30, 20, 1529),
        UnitEquipment(3, 3000, 3000, 33, 30, 80, 1529),
    ]


@pytest.fixture
def offers():
    return [
        RepairOffer(0, 101, "Offer 1", 200, 28, 1000),
        RepairOffer(1, 102, "Offer 2", 300, 31, 5000),
        RepairOffer(2, 103, "Offer 3", 100, 30, 10000),
        RepairOffer(3, 104, "Offer 4", 100, 29, 10000),
        RepairOffer(4, 105, "Offer 5", 200, 30, 10000),
        RepairOffer(5, 106, "Offer 6", 250, 33, 10000),
        RepairOffer(6, 107, "Offer 7", 400, 35, 10000),
    ]


def test_select_offer(offers, units):
    assert select_offer(offers, units) == offers[3]


def test_empty_offers_summary(units):
    with pytest.raises(NoSiutableOffersExists):
        select_offer([RepairOffer(0, 0, "company", 100, 1, 1000)], units)


def test_quantity_to_repair(units):
    assert quantity_to_repair(units) == 2850


def test_quantity_total(units):
    assert quantity_total(units) == 6000


@pytest.mark.parametrize(
    "unit, offer_id, count",
    [
        (
            UnitEquipment(0, 2000, 2000, 28.0, 30.0, 0.0, 1529),
            6,
            572,
        ),
        (
            UnitEquipment(0, 2000, 2000, 29.0, 31.0, 0.0, 1529),
            6,
            667,
        ),
    ],
)
def test_select_offer_to_raise_quality(offers, unit, offer_id, count):
    assert select_offer_to_raise_quality(unit, offers) == (offers[offer_id], count)


def test_select_offer_to_raise_quality_none(offers):
    unit = UnitEquipment(0, 2000, 2000, 29.0, 36.0, 0.0, 1529)
    assert select_offer_to_raise_quality(unit, offers) is None


def test_mismatched_quality(units_mismatch):
    normal, mismatched = split_mismatch_quality_units(units_mismatch)
    assert len(normal) == len(units_mismatch) - 1
    assert len(mismatched) == 1


def test_split_by_quality(units):
    res = split_by_quality(units)
    assert len(res) == 1
    res = split_by_quality(units, QualityType.INSTALLED)
    assert len(res) == 3


@pytest.mark.parametrize(
    "config_dict",
    [
        {"equipment_id": 0},
        {"equipment_id": 0, "exclude": [0], "quality": True},
        {"equipment_id": 0, "include": [0, 1], "offer_id": 0},
    ],
)
def test_repair_config(config_dict):
    config = RepairConfig(**config_dict)
    c = config.dict()
    for key, value in config_dict.items():
        assert key in c.keys()
        assert isinstance(config_dict[key], type(c[key]))


@pytest.fixture
def mock_equipment(offers):
    mock = Mock(spec=EquipmentGateway)
    mock.get_offers.return_value = offers
    return mock


def test_fix_mismatch_units(mock_equipment, units_mismatch, offers, options):
    action = RepairAction(mock_equipment, options)
    action.fix_units_quality(units_mismatch[:1])
    mock_equipment.terminate.assert_called_with(units_mismatch[0], 167)
    mock_equipment.buy.assert_called_with(units_mismatch[0], offers[6], 167)


def test_repair_with_quality(mock_equipment, units, offers, options):
    action = RepairAction(mock_equipment, options)
    action.repair_with_quality(units[:1], units[0].quality_required)
    mock_equipment.repair.assert_called_with(units[:1], offers[3])


def test_repair_by_quality(mock_equipment, units, offers, options):
    action = RepairAction(mock_equipment, options)
    action.repair_by_quality(units, QualityType.REQUIRED)
    mock_equipment.repair.assert_called_once()
