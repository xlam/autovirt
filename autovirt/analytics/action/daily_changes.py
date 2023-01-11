from autovirt.analytics.daily_changes.gateway.history import HistoryGateway
from autovirt.utils import get_logger


class DailyChangesAction:
    def __init__(self, history_gateway: HistoryGateway):
        self.gateway = history_gateway
        self.logger = get_logger()

    def run(self, limit: int):
        self.logger.info(f"Requesting financial histories...")
        histories = self.gateway.get_shops_finance_histories()
        for unit in sorted(histories)[:limit]:
            self.logger.info(
                f"{unit.name} {unit.id} ({unit.city_name}), change: {unit.change:<+1.2f}"
            )
