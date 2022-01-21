import abc


class EmployeeInterface(abc.ABC):
    @abc.abstractmethod
    def units(self) -> list:
        ...

    @abc.abstractmethod
    def unit_info(self, unit_id: int) -> dict:
        ...

    @abc.abstractmethod
    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        ...
