""" source: datalabs.access.vericre.util.profile """
import json

import mock
import pytest

from datalabs.access.api.task import InternalServerError
from datalabs.util import profile


# pylint: disable=redefined-outer-name, protected-access
def test_token_response_error(http_request_status_404, grant_type, client_id, client_secret, self=None):
    with mock.patch(
            'datalabs.util.profile._request_ama_token',
            return_value=http_request_status_404
    ), pytest.raises(Exception) as except_info:
        profile.get_ama_access_token(self, grant_type, client_id, client_secret)

    assert except_info.type == InternalServerError
    assert str(except_info.value) == \
           f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


@pytest.fixture
def http_request_status_404():
    response_data = "error data"
    response_reason = "error reason"
    mock_response = mock.Mock()
    mock_response.status = 404
    mock_response.data = response_data
    mock_response.reason = response_reason

    return mock_response


@pytest.fixture
def http_request_status_200():
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = json.dumps({"access_token": "token"})
    return mock_response


@pytest.fixture
def grant_type():
    return "grant_type"


@pytest.fixture
def client_id():
    return "client_id"


@pytest.fixture
def client_secret():
    return "client_secret"
