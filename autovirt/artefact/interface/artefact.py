import abc


class ArtefactGateway(abc.ABC):
    @abc.abstractmethod
    def attach(self, name, unit_id):
        pass
