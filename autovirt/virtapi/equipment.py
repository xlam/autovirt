from autovirt.equipment.interface import EquipmentGateway
from autovirt.exception import AutovirtError
from autovirt.session import VirtSession
from autovirt.structs import UnitEquipment, RepairOffer
from autovirt.utils import get_logger
from autovirt.virtapi import GatewayOptions

logger = get_logger()


class VirtEquipment(EquipmentGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def _fetch_units(self, equipment_id: int) -> list[dict]:
        """Fetch units equipment data"""
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/equipment/units",
            params={
                "id": self.options.company_id,
                "product_id": equipment_id,
                "pagesize": self.options.pagesize,
            },
        )
        return r.json()["data"].values()

    def _fetch_offers(self, product_id: int) -> list[dict]:
        """Fetch offers by product id"""
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/equipment/offers",
            params={
                "id": self.options.company_id,
                "product_id": product_id,
                "pagesize": self.options.pagesize,
            },
        )
        return r.json()["data"].values()

    def get_units_to_repair(self, equipment_id: int) -> list[UnitEquipment]:
        """Get units to repair by equipment.
        Only units whose equipment wear in greater than 0% will be returned
        """
        units_data = self._fetch_units(equipment_id)
        units = []
        for unit in units_data:
            if float(unit["equipment_wear"]) > 0:
                units.append(
                    UnitEquipment(
                        int(unit["id"]),
                        int(unit["equipment_quantity"]),
                        int(unit["equipment_quantity_max"]),
                        float(unit["equipment_quality"]),
                        float(unit["equipment_quality_required"]),
                        float(unit["equipment_wear"]),
                        int(unit["equipment_product_id"]),
                    )
                )
        return units

    def get_offers(self, product_id: int) -> list[RepairOffer]:
        """Get all offers for the product"""
        offers_data = self._fetch_offers(product_id)
        offers = []
        for offer in offers_data:
            offers.append(
                RepairOffer(
                    int(offer["id"]),
                    int(offer["company_id"]),
                    str(offer["company_name"]),
                    float(offer["price"]),
                    float(offer["quality"]),
                    int(offer["quantity"]),
                )
            )
        return offers

    def repair(self, units: list[UnitEquipment], offer: RepairOffer):
        """Do repair of units equpment with offer provided"""

        params = [("units_ids[]", unit.id) for unit in units]
        params.append(("id", self.options.company_id))
        params.append(("offer_id", offer.id))
        r = self.s.post(
            "https://virtonomica.ru/api/vera/main/company/equipment/repair",
            params=params,
        )
        logger.info(f"Virtonomica API response: {r.json()}")
        if not r.ok:
            raise AutovirtError(f"could not repair, status code: {r.status_code}")

    def terminate(self, unit: UnitEquipment, quantity: int):
        r = self.s.post(
            "https://virtonomica.ru/api/vera/main/unit/equipment/terminate",
            {
                "id": unit.id,
                "token": self.s.token,
                "qty": quantity,
            },
        )
        if not r.ok:
            raise AutovirtError(
                f"could not terminate equipment, status code: {r.status_code}"
            )

    def buy(self, unit: UnitEquipment, offer: RepairOffer, quantity: int):
        r = self.s.post(
            "https://virtonomica.ru/api/vera/main/unit/equipment/update",
            {
                "offer_id": offer.id,
                "id": unit.id,
                "token": self.s.token,
                "operation_name": "buy",
                "equipment_count": quantity,
            },
        )
        if not r.ok:
            raise AutovirtError(
                f"could not buy equipment, status code: {r.status_code}"
            )
