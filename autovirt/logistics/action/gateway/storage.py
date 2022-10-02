import abc

from autovirt.logistics.domain import StorageItem


class StorageGateway(abc.ABC):
    @abc.abstractmethod
    def get(self, unit_id: int) -> list[StorageItem]:
        pass

    @abc.abstractmethod
    def set_supplies(self, storage: list[StorageItem]):
        pass
