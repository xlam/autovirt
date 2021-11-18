from autovirt.action.repair import (
    quantity_total,
    quantity_to_repair,
    get_min,
    get_max,
    select_offer,
)
from autovirt.structs import UnitEquipment, RepairOffer

offers = [
    RepairOffer(0, 101, "Offer 1", 200, 32, 1000),
    RepairOffer(1, 102, "Offer 2", 300, 31, 5000),
    RepairOffer(2, 103, "Offer 3", 100, 30, 10000),
    RepairOffer(3, 104, "Offer 4", 100, 29, 10000),
    RepairOffer(4, 105, "Offer 5", 200, 30, 10000),
]
units = [
    UnitEquipment(1, 1000, 1000, 31, 30, 5, 1529),
    UnitEquipment(2, 2000, 2000, 32, 30, 20, 1529),
    UnitEquipment(3, 3000, 3000, 33, 30, 80, 1529),
]


def test_select_offer():
    assert select_offer(offers, units) == offers[3]


def test_quantity_to_repair():
    assert quantity_to_repair(units) == 2850


def test_quantity_total():
    assert quantity_total(units) == 6000


def test_min_quality():
    assert get_min(units, "qual") == 31


def test_max_quality():
    assert get_max(units, "qual") == 33


def test_min_price():
    assert get_min(offers, "price") == 100
