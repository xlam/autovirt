from autovirt import utils
import config

logger = utils.get_logger("virtapi.employee")
s = utils.get_logged_session()
token = utils.get_token(s)


def units():
    r = s.get(
        f"https://virtonomica.ru/api/vera/main/company/employee/units?"
        f"id={config.company_id}"
        f"&pagesize={config.pagesize}"
    )
    return list(r.json()["data"].values())


def unit_info(unit_id: int) -> dict:
    r = s.get(f"https://virtonomica.ru/api/vera/main/unit/employee/info?id={unit_id}")
    return r.json()


def set_salary(unit_id: int, employee_count: int, salary: float):
    s.post(
        f"https://virtonomica.ru/api/vera/main/unit/employee/update",
        {
            "id": unit_id,
            "employee_count": employee_count,
            "employee_salary": salary,
            "token": token,
        },
    )
