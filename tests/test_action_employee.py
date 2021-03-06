from unittest.mock import patch, call

import pytest

from autovirt.employee.domain import units_to_rise_salary
from autovirt.employee.set_demanded_salary import SetDemandedSalaryAction
from autovirt.structs import Message


@pytest.fixture
def messages() -> list[Message]:
    return [
        Message(
            0,
            "Недовольство заработной платой",
            "message_body",
            0,
            [
                {"object_id": 0, "object_name": "Unit 0", "tag": 100},
                {"object_id": 1, "object_name": "Unit 1", "tag": 200},
                {"object_id": 2, "object_name": "Unit 2", "tag": 300},
            ],
        ),
        Message(1, "subject", "body", 0, []),
    ]


def test_units_to_raise_salary(messages):
    assert len(units_to_rise_salary(messages[:1])) == len(messages[0].attaches)


@patch("autovirt.employee.set_demanded_salary.EmployeeGateway")
@patch("autovirt.employee.set_demanded_salary.MailGateway")
def test_rise_salary(mail_mock, employee_mock, messages):
    mail_mock.get_messages_by_subject.return_value = messages[:1]
    employee_mock.unit_info.return_value = {"employee_salary": 90, "employee_max": 1000}
    employee = SetDemandedSalaryAction(mail_mock, employee_mock)
    employee.rise_salary()
    employee_mock.assert_has_calls(
        [
            call.set_salary(0, 1000, 105),
            call.set_salary(1, 1000, 205),
            call.set_salary(2, 1000, 305),
        ],
        any_order=True,
    )
    mail_mock.delete_messages.assert_called_with(messages[:1])
