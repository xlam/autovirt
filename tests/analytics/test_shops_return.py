from autovirt.analytics.daily_changes.domain.history_entry import HistoryEntry
from autovirt.analytics.daily_changes.domain.unit_history import UnitHistory
from autovirt.analytics.daily_changes.gateway.history import HistoryGateway


class FakeHistoryGateway(HistoryGateway):
    def get_shops_finance_histories(self) -> list[UnitHistory]:
        return [
            UnitHistory(
                1, "Unit1", "City1", [HistoryEntry(0, 20), HistoryEntry(1, 10)]
            ),
            UnitHistory(
                2, "Unit2", "City2", [HistoryEntry(0, 10), HistoryEntry(1, 30)]
            ),
            UnitHistory(
                3, "Unit3", "City3", [HistoryEntry(0, 10), HistoryEntry(1, 15)]
            ),
        ]


def test_daily_returns():
    history_gateway = FakeHistoryGateway()
    histories = history_gateway.get_shops_finance_histories()
    for unit in sorted(histories[:5]):
        print(f"{unit.name} {unit.id} ({unit.city_name}), change: {unit.change:<+1.2f}")
