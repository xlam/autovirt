from autovirt.utils import get_config
from autovirt.session import VirtSession

_config = get_config("autovirt")
s = VirtSession()


def units():
    r = s.get(
        "https://virtonomica.ru/api/vera/main/company/employee/units",
        params={"id": _config["company_id"], "pagesize": _config["pagesize"]},
    )
    return list(r.json()["data"].values())


def unit_info(unit_id: int) -> dict:
    r = s.get(
        "https://virtonomica.ru/api/vera/main/unit/employee/info",
        params={"id": unit_id},
    )
    return r.json()


def set_salary(unit_id: int, employee_count: int, salary: float):
    s.post(
        f"https://virtonomica.ru/api/vera/main/unit/employee/update",
        {
            "id": unit_id,
            "employee_count": employee_count,
            "employee_salary": salary,
            "token": s.token,
        },
    )
