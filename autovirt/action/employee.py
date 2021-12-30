from typing import Optional

from autovirt import utils
from autovirt.action.interface import MailInterface, EmployeeInterface
from autovirt.structs import Message

logger = utils.get_logger()


def units_to_rise_salary(messages: list[Message]) -> list:
    units = []
    for message in messages:
        for attach in message.attaches:
            units.append(
                {
                    "id": attach["object_id"],
                    "name": attach["object_name"],
                    "salary_demanded": float(attach["tag"]),
                }
            )
    return units


class EmployeeAction:

    subject: str = "Недовольство заработной платой"

    def __init__(
        self, mail_gateway: MailInterface, employee_gateway: EmployeeInterface
    ):
        self.mail = mail_gateway
        self.employee = employee_gateway

    def rise_salary(self):
        messages = self.mail.get_messages(self.subject)
        if not messages:
            logger.info("no units to rise salary, exiting.")
            return
        units = units_to_rise_salary(messages)

        for unit in units:
            data = self.employee.unit_info(int(unit["id"]))
            salary = round(unit["salary_demanded"]) + 5
            logger.info(
                f"raising salary at {unit['name']} ({unit['id']}) "
                f"from {data['employee_salary']} to {salary}"
            )
            self.employee.set_salary(int(unit["id"]), int(data["employee_max"]), salary)

        self.mail.delete_messages(messages)

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass
        self.rise_salary()
