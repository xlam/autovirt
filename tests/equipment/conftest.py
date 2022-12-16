from unittest.mock import Mock

import pytest

from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment


@pytest.fixture
def units():
    return [
        UnitEquipment(1, 1000, 1000, 31, 30, 5, 1529),
        UnitEquipment(2, 2000, 2000, 32, 30, 20, 1529),
        UnitEquipment(3, 3000, 3000, 33, 30, 80, 1529),
    ]


@pytest.fixture
def units_mismatch():
    return [
        UnitEquipment(1, 1000, 1000, 29, 30, 5, 1529),
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


@pytest.fixture
def mock_equipment(offers):
    mock = Mock(spec=EquipmentGateway)
    mock.get_offers.return_value = offers
    return mock
