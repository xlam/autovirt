from typing import Protocol

from autovirt.structs import Message


class MailInterface(Protocol):
    def get_messages(self, subject: str) -> list[Message]:
        ...

    def delete_messages(self, messages: list[Message]):
        ...
