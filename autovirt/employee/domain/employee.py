from autovirt.structs import Message


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


def units_to_update_salary(units: list) -> list[dict]:
    res = []
    for unit in units:
        if float(unit["labor_level"]) < float(unit["employee_level_required"]):
            res.append(unit)
    return res
