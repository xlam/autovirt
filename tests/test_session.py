from unittest.mock import patch
import requests
from autovirt.session import VirtSession


@patch("autovirt.session.VirtSession.login")
def test_get_logged_session(login_mock):
    session = VirtSession()
    assert type(session.get_logged_session()) == requests.Session
    login_mock.assert_called()


@patch("autovirt.session.requests.Session.post")
def test_login_success(post_mock):
    response = requests.Response()
    response.status_code = 200
    post_mock.return_value = response
    session = VirtSession(requests.Session())
    session.login()
    post_mock.assert_called()
