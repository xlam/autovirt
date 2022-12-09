from unittest.mock import Mock

import pytest

from autovirt.mail.domain.message import Message
from autovirt.mail.adapter.api_mail import ApiMailAdapter


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


def test_get_messages(messages_dict):
    mail = ApiMailAdapter(Mock())
    mail._fetch_messages = Mock(return_value=messages_dict)
    messages = mail.get_messages_by_subject()
    assert len(messages) == len(messages_dict)
    assert isinstance(messages[0], Message)
