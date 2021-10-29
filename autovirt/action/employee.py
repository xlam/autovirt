from autovirt import utils
from autovirt.virtapi import mail
from autovirt.virtapi import employee
from autovirt.structs import Message


logger = utils.get_logger("employee")


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


def rise_salary():
    messages = mail.get_messages(subject="Недовольство заработной платой")
    if not messages:
        logger.info("no units to rise salary, exiting.")
        return
    units = units_to_rise_salary(messages)

    for unit in units:
        data = employee.unit_info(int(unit["id"]))
        salary = round(unit["salary_demanded"]) + 5
        logger.info(
            f"raising salary at {unit['name']} ({unit['id']}) "
            f"from {data['employee_salary']} to {salary}"
        )
        employee.set_salary(int(unit["id"]), int(data["employee_max"]), salary)

    mail.delete_messages(messages)


def run(config_name):
    if not config_name:
        pass

    logger.info("starting salary rising")
    rise_salary()
    logger.info("finished salary rising")
