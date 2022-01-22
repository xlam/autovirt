import abc

from autovirt.structs import Message


class MailGateway(abc.ABC):
    @abc.abstractmethod
    def get_messages(self, subject: str) -> list[Message]:
        pass

    @abc.abstractmethod
    def delete_messages(self, messages: list[Message]):
        pass
