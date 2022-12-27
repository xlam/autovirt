from typing import Protocol


class UnitsGateway(Protocol):
    def get_shops_ids(self) -> list[int]:
        ...
