from autovirt import utils
from autovirt.virtapi import employee


logger = utils.get_logger("salary")
s = utils.get_logged_session()
token = utils.get_token(s)


def units_to_update_salary() -> list[dict]:
    data = employee.units()
    units = []
    for unit in data:
        if float(unit["labor_level"]) < float(unit["employee_level_required"]):
            units.append(unit)
    return units


def run(config_name):
    if not config_name:
        pass

    logger.info("starting salary update")

    units = units_to_update_salary()

    if not units:
        logger.info("no units to update salary, exiting.")
        quit(0)
    logger.info(f"{len(units)} units to update salary")

    for unit in units:
        unit_info = employee.unit_info(unit["id"])
        # set salary to required plus 5$ for sure
        salary = round(unit_info["salary_required"]) + 5
        logger.info(
            f"updating salary at unit "
            f"{unit['id']} ({unit['name']}, {unit['city_name']}) from "
            f"{unit['labor_salary']} to {salary}"
        )
        employee.set_salary(int(unit["id"]), int(unit_info["employee_max"]), salary)
