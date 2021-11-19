import pytest
from autovirt.utils import normalize


@pytest.mark.parametrize(
    "x, xmin, xmax, res", [(5, 0, 10, 0.5), (5, 5, 10, 0), (10, 5, 10, 1), (5, 5, 5, 0)]
)
def test_normalize(x, xmin, xmax, res):
    assert normalize(x, xmin, xmax) == res


def test_normalize_value_error():
    with pytest.raises(ValueError):
        normalize(20, 0, 10)
