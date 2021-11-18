import pytest
from autovirt.structs import UnitEquipment


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


@pytest.mark.parametrize(
    "quality, expected", [(35.124, 12), (35.126, 13), (35.125, 12)]
)
def test_unit_equipment_floats_rounded(quality: float, expected: int):
    ue = UnitEquipment(
        1,
        100,
        100,
        quality,
        35,
        0,
        1234,
    )
    quality_string = str(ue.qual)
    decimal = int(quality_string.split(".")[1])
    assert decimal == expected


@pytest.mark.parametrize("wear, quality, expected", [(0, 40, 31), (5, 40, 31.45)])
def test_unit_equipment_calculates_expected_quality(
    ue, wear: float, quality: float, expected: float
):
    ue.wear = wear
    assert ue.expected_quality(quality) == expected
