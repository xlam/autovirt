from autovirt import utils
from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.unitsupplies import Supply, SupplyContract, UnitSupplies
from autovirt.session import VirtSession


logger = utils.get_logger()


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
                int(item["quantity"]),
                int(item["required"]),
                [
                    SupplyContract(
                        consumer_id=int(contract["consumer_id"]),
                        offer_id=offer_id,
                        supplier_id=int(contract["supplier_id"]),
                        free_for_buy=int(contract["free_for_buy"]),
                        party_quantity=int(contract["party_quantity"]),
                    )
                    for offer_id, contract in item["contracts"].items()
                ],
            )
            supplies.append(supply)
        return UnitSupplies(supplies)

    def set_supplies(self, supplies: UnitSupplies):
        url = "https://virtonomica.ru/api/vera/main/unit/supply/set"
        for supply in supplies:
            for contract in supply.contracts:
                params = {
                    "id": contract.consumer_id,
                    "offer_id": contract.offer_id,
                    "qty": contract.party_quantity,
                    "token": self.s.token,
                }
                logger.info(
                    f"ordering {contract.party_quantity} pieces of {supply.product_id} to unit {contract.consumer_id}"
                )
                r = self.s.post(url, params)
                logger.info(f"response: {r}")
