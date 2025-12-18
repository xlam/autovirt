import os
from unittest.mock import patch

import pytest
import requests

from autovirt.session import VirtSession, VirtSessionOptions


@pytest.fixture
def options() -> VirtSessionOptions:
    return VirtSessionOptions(
        session_file="tests/session.dat",
        session_timeout=1800,
        base_url="https://virtonomica.ru/api/vera",
        login="login",
        password="password",
    )


@pytest.fixture
def response_ok() -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    return response


@pytest.fixture
def response_not_ok() -> requests.Response:
    response = requests.Response()
    response.status_code = 500
    return response


@pytest.fixture
def session(options):
    return VirtSession(options=options)


@patch("autovirt.session.VirtSession.login")
def test_get_logged_session_new_session(login_mock, session):
    if os.path.isfile(session.options.session_file):
        os.remove(session.options.session_file)
    assert type(session.get_logged_session()) == requests.Session
    login_mock.assert_called()


@patch("autovirt.session.requests.Session.post")
def test_login_response_ok(
    post_mock, session, options: VirtSessionOptions, response_ok
):
    post_mock.return_value = response_ok
    session.login(requests.Session())
    post_mock.assert_called_with(
        f"{options.base_url}/main/user/login",
        data={"email": options.login, "password": options.password},
    )


@patch("autovirt.session.requests.Session.post")
def test_login_response_not_ok(
    post_mock, session, options: VirtSessionOptions, response_not_ok
):
    post_mock.return_value = response_not_ok
    with pytest.raises(RuntimeError):
        session.login(requests.Session())
