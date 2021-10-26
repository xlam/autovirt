from dataclasses import dataclass


@dataclass
class UnitEquipment:
    id: str
    qnt: str
    qnt_max: str
    qual: str
    qual_req: str
    wear: str
    equipment_id: str


@dataclass
class RepairOffer:
    id: str
    price: float
    quality: float
    quantity: int
