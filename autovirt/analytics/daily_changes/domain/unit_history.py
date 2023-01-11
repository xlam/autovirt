from dataclasses import dataclass

from .history_entry import HistoryEntry


@dataclass
class UnitHistory:
    id: int
    name: str
    city_name: str
    history: list[HistoryEntry]

    @property
    def change(self):
        if len(self.history) < 2:
            return 0
        return self.history[-1].income - self.history[-2].income

    def __gt__(self, other):
        return abs(self.change) < abs(other.change)
