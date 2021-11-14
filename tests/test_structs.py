import pytest
from autovirt.structs import UnitEquipment


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
