import pytest
from autovirt.action.repair import (
    quantity_total,
    quantity_to_repair,
    select_offer,
    select_offer_to_raise_quality,
    split_mismatch_quality_units,
    split_by_quality,
)
from autovirt.structs import UnitEquipment, RepairOffer


@pytest.fixture
def units():
    return [
        UnitEquipment(1, 1000, 1000, 31, 30, 5, 1529),
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


def test_mismatched_quality(units):
    normal, mismatched = split_mismatch_quality_units(units, 31.5)
    assert len(normal) == 2
    assert len(mismatched) == 1


def test_split_by_quality(units):
    res = split_by_quality(units)
    assert len(res) == 1
    res = split_by_quality(units, "qual")
    assert len(res) == 3
