import pytest
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
