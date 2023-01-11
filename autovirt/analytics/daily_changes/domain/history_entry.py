from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryEntry:
    turn: int
    income: float
