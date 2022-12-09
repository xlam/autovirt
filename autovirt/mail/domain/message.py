from dataclasses import dataclass


@dataclass
class Message:
    id: int
    subject: str
    body: str
    status: int
    attaches: list[dict]
