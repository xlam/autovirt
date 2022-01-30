import pytest
from unittest.mock import patch
from autovirt.structs import Message
from autovirt.virtapi.mail import VirtMail


@pytest.fixture
def messages_dict() -> dict:
    return {
        "0": {
            "id": "0",
            "created": "2021-12-29 06:55:00.160933",
            "lifetime": "5",
            "from_user": None,
            "from_user_name": None,
            "to_user": "1",
            "to_user_name": "username",
            "prev_message": None,
            "next_message": None,
            "subject": "subject0",
            "body": "body0",
            "status": "0",
            "category": None,
            "attaches": [],
            "contracts": [],
        },
        "1": {
            "id": "1",
            "created": "2021-12-29 06:55:00.160933",
            "lifetime": "5",
            "from_user": None,
            "from_user_name": None,
            "to_user": "1",
            "to_user_name": "username",
            "prev_message": None,
            "next_message": None,
            "subject": "subject1",
            "body": "body1",
            "status": "0",
            "category": None,
            "attaches": [],
            "contracts": [],
        },
    }


@patch("autovirt.virtapi.mail.VirtSession")
@patch("autovirt.virtapi.mail.VirtMail._fetch_messages")
def test_get_messages(fetch_mock, session_mock, messages_dict):
    mail = VirtMail(session_mock)
    fetch_mock.return_value = messages_dict
    messages = mail.get_messages()
    assert len(messages) == len(messages_dict)
    assert isinstance(messages[0], Message)
