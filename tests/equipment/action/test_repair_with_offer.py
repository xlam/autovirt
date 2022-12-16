from autovirt.equipment.action.repair_with_offer import RepairWithOfferInputDTO
from autovirt.equipment.action.repair_with_offer import RepairWithOfferAction


def test_adapter_called_with_offer(mock_equipment, units, offers):
    action = RepairWithOfferAction(mock_equipment)
    mock_equipment.get_units_to_repair.return_value = units
    mock_equipment.get_offer_by_id.return_value = offers[0]
    input_dto = RepairWithOfferInputDTO(equipment_id=1529, offer_id=0)
    action.run(input_dto=input_dto)
    mock_equipment.repair.assert_called_once_with(units, offers[0])
