from typing import Optional

from autovirt.equipment.action.gateway import EquipmentGateway
from autovirt.equipment.domain.repair_offer import RepairOffer
from autovirt.equipment.domain.unit_equipment import UnitEquipment
from autovirt.exception import AutovirtError
from autovirt.gateway_options import GatewayOptions
from autovirt.session import VirtSession
from autovirt.utils import get_logger

logger = get_logger()


class ApiEquipmentAdapter(EquipmentGateway):
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

    def _fetch_offers(self, unit_id: int, quantity_from: int = 0) -> list[dict]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/equipment/offers",
            params={
                "id": unit_id,
                "quantity_from": quantity_from,
                "pagesize": self.options.pagesize,
            },
        )
        return r.json()["data"].values()

    def get_units_to_repair(
        self,
        equipment_id: int,
        units_only: list[int] = None,
        units_exclude: list[int] = None,
    ) -> list[UnitEquipment]:
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

            if units_only:
                units = list(filter(lambda x: x.id in units_only, units))  # type: ignore

            if units_exclude:
                units = list(filter(lambda x: x.id not in units_exclude, units))  # type: ignore

        return units

    def get_offers(self, unit_id: int, quantity_from: int = 0) -> list[RepairOffer]:
        """Get all offers for the product"""
        offers_data = self._fetch_offers(unit_id, quantity_from)
        offers = []
        for offer in offers_data:
            offers.append(
                RepairOffer(
                    int(offer["id"]),
                    int(offer["company_id"]),
                    str(offer["company_name"]),
                    float(offer["total_cost"]),
                    float(offer["quality"]),
                    int(offer["free_for_buy"]),
                )
            )
        return offers

    def get_offer_by_id(self, unit_id, offer_id) -> Optional[RepairOffer]:
        offers = self.get_offers(unit_id, quantity_from=1)
        for offer in offers:
            if offer.id == offer_id:
                return offer
        return None

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
