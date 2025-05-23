from autovirt import utils
from autovirt.logistics.action.gateway import SuppliesGateway
from autovirt.logistics.domain.supplies.unit_supplies import UnitSupplies
from autovirt.logistics.domain.supplies.supply import Supply
from autovirt.logistics.domain.supplies.contract import Contract
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
                unit_id,
                int(item["product_id"]),
                item["product_name"],
                int(item["quantity"]),
                int(item["required"]),
                [
                    Contract(
                        consumer_id=int(contract["consumer_id"]),
                        offer_id=int(offer_id),
                        supplier_id=int(contract["supplier_id"]),
                        free_for_buy=int(contract["free_for_buy"]),
                        party_quantity=int(contract["party_quantity"]),
                    )
                    for offer_id, contract in item["contracts"].items()
                ],
            )
            supplies.append(supply)
        return UnitSupplies(unit_id, supplies)

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
                r = self.s.post(url, params)
                logger.info(f"response: {r}")
