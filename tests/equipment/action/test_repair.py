from unittest.mock import Mock

import pytest

from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.action.repair import (
    RepairInputDTO,
    RepairAction,
)
from autovirt.equipment.domain.equipment import QualityType
from autovirt.equipment.domain.repair_offer import RepairOffer


@pytest.fixture
def offers_for_installed():
    return [
        [
            RepairOffer(0, 101, "Offer 1", 200, 28, 1000),
            RepairOffer(1, 102, "Offer 2", 300, 31, 5000),
            RepairOffer(2, 103, "Offer 3", 100, 30, 10000),
        ],
        [],
        [
            RepairOffer(4, 105, "Offer 5", 200, 30, 10000),
            RepairOffer(5, 106, "Offer 6", 250, 33, 10000),
            RepairOffer(6, 107, "Offer 7", 400, 35, 10000),
        ],
    ]


@pytest.fixture
def mock_equipment(offers):
    mock = Mock(spec=EquipmentGateway)
    mock.get_offers.return_value = offers
    return mock


@pytest.fixture
def mock_equipment_for_installed(offers_for_installed):
    mock = Mock(spec=EquipmentGateway)
    mock.get_offers.side_effect = offers_for_installed
    return mock


@pytest.mark.parametrize(
    "config_dict",
    [
        {"equipment_id": 0},
        {"equipment_id": 0, "units_exclude": [0], "keep_quality": True},
        {"equipment_id": 0, "units_only": [0, 1], "offer_id": 0},
    ],
)
def test_repair_config(config_dict):
    config = RepairInputDTO(**config_dict)
    c = config.dict()
    for key, value in config_dict.items():
        assert key in c.keys()
        assert isinstance(config_dict[key], type(c[key]))


def test_fix_mismatch_units(mock_equipment, units_mismatch, offers):
    action = RepairAction(mock_equipment)
    action.fix_units_quality(units_mismatch[:1])
    mock_equipment.terminate.assert_called_with(units_mismatch[0], 167)
    mock_equipment.buy.assert_called_with(units_mismatch[0], offers[6], 167)


def test_repair_with_quality(mock_equipment, units, offers):
    action = RepairAction(mock_equipment)
    action.repair_with_quality(units[:1], units[0].quality_required)
    mock_equipment.repair.assert_called_with(units[:1], offers[3])


def test_repair_by_required_quality(mock_equipment, units, offers):
    action = RepairAction(mock_equipment)
    action.repair_by_quality(units, QualityType.REQUIRED)
    mock_equipment.repair.assert_called_once()


def test_repair_by_installed_quality(mock_equipment_for_installed, units, offers):
    action = RepairAction(mock_equipment_for_installed)
    action.repair_by_quality(units, QualityType.INSTALLED)
    assert mock_equipment_for_installed.repair.call_count == 2
