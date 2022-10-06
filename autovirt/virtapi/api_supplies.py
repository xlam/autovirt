from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.unitsupplies import Supply, SupplyContract, UnitSupplies
from autovirt.session import VirtSession


class ApiSuppliesGateway(SuppliesGateway):
    def __init__(self, session: VirtSession):
        self.s = session

    def get(self, unit_id: int) -> UnitSupplies:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/supply/summary",
            params={"id": unit_id},
        )
        supplies_data = list(r.json().values())
        supplies = []
        for item in supplies_data:
            if "contracts" not in item.keys():
                item["contracts"] = {}
            supply = Supply(
                int(item["product_id"]),
                int(item["available"]),
                int(item["required"]),
                [
                    SupplyContract(
                        consumer_id=contract["consumer_id"],
                        offer_id=offer_id,
                        supplier_id=contract["supplier_id"],
                        free_for_buy=contract["free_for_buy"],
                        party_quantity=contract["party_quantity"],
                    )
                    for offer_id, contract in item["contracts"].items()
                ],
            )
            supplies.append(supply)
        return UnitSupplies(supplies)

    def set_supplies(self, supplies: UnitSupplies):
        pass
