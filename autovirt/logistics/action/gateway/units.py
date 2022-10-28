import abc


class UnitsGateway(abc.ABC):
    @abc.abstractmethod
    def get_shops_ids(self) -> list[int]:
        pass
