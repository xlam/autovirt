import abc

from autovirt.structs import Message


class MailInterface(abc.ABC):
    @abc.abstractmethod
    def get_messages(self, subject: str) -> list[Message]:
        ...

    @abc.abstractmethod
    def delete_messages(self, messages: list[Message]):
        ...
