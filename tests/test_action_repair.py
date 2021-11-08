from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.action.repair import get_offers_by_quality


offers = [RepairOffer(1, 100, 30, 1000)]
units = {
    29: [
        UnitEquipment(1, 10, 10, 29, 29, 0.1, 1529),
        UnitEquipment(2, 10, 10, 29, 29, 0.1, 1529),
        UnitEquipment(3, 10, 10, 29, 29, 0.1, 1529),
    ],
    31: [
        UnitEquipment(4, 10, 10, 29, 31, 0.1, 1529),
        UnitEquipment(5, 10, 10, 29, 31, 0.1, 1529),
        UnitEquipment(6, 10, 10, 29, 31, 0.1, 1529),
    ],
}


def test_get_offers_by_quality():
    result = get_offers_by_quality(units, offers)
    assert len(result) == 1
    assert len(list(result.values())[0]) == 6
    assert result == {offers[0]: units[29] + units[31]}
