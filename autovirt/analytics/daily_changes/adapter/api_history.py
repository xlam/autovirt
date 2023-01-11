import time

from autovirt.analytics.daily_changes.domain.history_entry import HistoryEntry
from autovirt.analytics.daily_changes.domain.unit_history import UnitHistory
from autovirt.analytics.daily_changes.gateway.history import HistoryGateway
from autovirt.gateway_options import GatewayOptions
from autovirt.session import VirtSession

REQUEST_DELAY = 0.1


class ApiHistoryGateway(HistoryGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def _fetch_shops(self) -> list[dict]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/units",
            params={
                "id": self.options.company_id,
                "unit_class_id": 1885,
                "pagesize": self.options.pagesize,
            },
        )
        return r.json()["data"].values()

    def _fetch_history(self, shop_id) -> list[dict]:
        time.sleep(REQUEST_DELAY)
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/report/finance/flow",
            params={
                "id": shop_id,
            },
        )
        return r.json()

    def get_shops_finance_histories(self) -> list[UnitHistory]:
        histories = []
        for shop in self._fetch_shops():
            history = self._fetch_history(int(shop["id"]))
            histories.append(
                UnitHistory(
                    int(shop["id"]),
                    shop["name"],
                    shop["city_name"],
                    [
                        HistoryEntry(int(turn), float(data["income"]))
                        for turn, data in enumerate(history)
                    ],
                )
            )
        return histories
