from unittest.mock import patch
import pytest
import requests

from autovirt.session import VirtSession

CONFIG = {"session_file": "tests/session.dat", "login": "email", "password": "password"}


@pytest.fixture
def response_ok():
    response = requests.Response()
    response.status_code = 200
    return response


@patch("autovirt.session.VirtSession.login")
def test_get_logged_session(login_mock):
    session = VirtSession(config=CONFIG)
    assert type(session.get_logged_session()) == requests.Session
    login_mock.assert_called()


@patch("autovirt.session.requests.Session.post")
def test_login_success(post_mock, response_ok):
    post_mock.return_value = response_ok
    session = VirtSession(session=requests.Session(), config=CONFIG)
    session.login()
    post_mock.assert_called_with(
        f"{session.BASE_URL}/user/login",
        {"email": CONFIG["login"], "password": CONFIG["password"]},
    )
