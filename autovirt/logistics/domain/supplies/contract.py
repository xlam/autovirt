from dataclasses import dataclass


@dataclass
class Contract:
    consumer_id: int
    offer_id: int
    supplier_id: int
    free_for_buy: int
    party_quantity: int
