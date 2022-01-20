import abc


class ArtefactInterface(abc.ABC):
    @abc.abstractmethod
    def attach(self, name, unit_id):
        ...
