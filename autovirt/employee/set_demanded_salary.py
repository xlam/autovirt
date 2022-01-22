from typing import Optional

from autovirt import utils
from autovirt.employee.domain import units_to_rise_salary
from autovirt.employee.interface import EmployeeGateway
from autovirt.mail.interface import MailGateway

logger = utils.get_logger()


class SetDemandedSalaryAction:
    SALARY_MARGIN: float = 5.0
    """ Salary margin to add to demanded salary value"""

    subject: str = "Недовольство заработной платой"
    """ Mail subject to filter units demanding salary raise"""

    def __init__(self, mail_gateway: MailGateway, employee_gateway: EmployeeGateway):
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
            salary = round(unit["salary_demanded"]) + self.SALARY_MARGIN
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
