import pytest

from autovirt.equipment.domain.equipment import (
    select_offer,
    quantity_to_repair,
    quantity_total,
    select_offer_to_raise_quality,
    split_mismatch_required_quality_units,
    split_by_quality,
    QualityType,
)
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment


@pytest.fixture()
def ue():
    return UnitEquipment(
        1,  # id
        100,  # quantity
        100,  # quantity max
        31,  # quality installed
        30,  # quality required
        0,  # equipment wear, %
        1234,  # equipment id
    )


@pytest.mark.parametrize("wear, quality, expected", [(0, 40, 31), (5, 40, 31.45)])
def test_unit_equipment_calculates_expected_quality(
    ue, wear: float, quality: float, expected: float
):
    ue.wear = wear
    assert ue.expected_quality(quality) == expected


def test_select_offer(offers, units):
    assert select_offer(offers, units) == offers[3]


def test_empty_offers_summary(units):
    assert select_offer([RepairOffer(0, 0, "company", 100, 1, 1000)], units) is None


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
    assert select_offer_to_raise_quality(unit, offers) == (None, None)

    offers_ = [RepairOffer(1, 1, "Offer1", 400, 40.0, 1)]
    assert select_offer_to_raise_quality(unit, offers_) == (None, None)


def test_mismatched_quality(units_mismatch):
    normal, mismatched = split_mismatch_required_quality_units(units_mismatch)
    assert len(normal) == len(units_mismatch) - 1
    assert len(mismatched) == 1


def test_split_by_quality(units):
    res = split_by_quality(units)
    assert len(res) == 1
    res = split_by_quality(units, QualityType.INSTALLED)
    assert len(res) == 3
