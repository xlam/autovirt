from dataclasses import dataclass

import pytest

from autovirt.utils import normalize, normalize_array, get_min, get_max


@pytest.fixture
def entities():
    @dataclass
    class Entity:
        f1: int
        f2: float
        f3: str

    return [
        Entity(1, 1.0, "1"),
        Entity(2, 2.0, "2"),
        Entity(3, 3.0, "3"),
    ]


@pytest.mark.parametrize(
    "x, xmin, xmax, res", [(5, 0, 10, 0.5), (5, 5, 10, 0), (10, 5, 10, 1), (5, 5, 5, 0)]
)
def test_normalize(x, xmin, xmax, res):
    assert normalize(x, xmin, xmax) == res


def test_normalize_value_error():
    with pytest.raises(ValueError):
        normalize(20, 0, 10)


def test_normalize_array_empty_error():
    with pytest.raises(ValueError):
        normalize_array([])


@pytest.mark.parametrize(
    "arr, res",
    [
        ((2, 7, 0, 4, 8, 10), [0.2, 0.7, 0.0, 0.4, 0.8, 1.0]),
        ((1, 1), [0, 0]),
        ((1,), [0]),
    ],
)
def test_normalize_array(arr, res):
    assert normalize_array(arr) == res


@pytest.mark.parametrize("field, result", [("f1", 1), ("f2", 1.0), ("f3", "1")])
def test_min(entities, field, result):
    assert get_min(entities, field) == result


@pytest.mark.parametrize("field, result", [("f1", 3), ("f2", 3.0), ("f3", "3")])
def test_max(entities, field, result):
    assert get_max(entities, field) == result
