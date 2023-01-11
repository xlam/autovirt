from typing import Protocol

from autovirt.analytics.daily_changes.domain.unit_history import UnitHistory


class HistoryGateway(Protocol):
    def get_shops_finance_histories(self) -> list[UnitHistory]:
        ...
