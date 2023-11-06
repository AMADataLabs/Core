""" source: datalabs.access.vericre.authentication """
import pytest
import mock

from datalabs.access.api.task import InternalServerError
from datalabs.access.vericre.api.authentication import PassportAuthenticatingEndpointMixin


# pylint: disable=redefined-outer-name, protected-access
def test_token_response_error(passport_mixin, parameters, http_request_status_404, self=None):
    with mock.patch(
            'datalabs.access.vericre.api.authentication.PassportAuthenticatingEndpointMixin._request_ama_token',
            return_value=http_request_status_404
    ), pytest.raises(Exception) as except_info:
        passport_mixin._get_passport_access_token(parameters)

    assert except_info.type == InternalServerError
    assert str(except_info.value) == \
           f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


def test_get_token(passport_mixin, http_request_status_200, parameters, self=None):
    with mock.patch(
            'datalabs.access.vericre.api.authentication.PassportAuthenticatingEndpointMixin._request_ama_token',
            return_value=http_request_status_200
    ):
        with mock.patch('datalabs.access.vericre.api.authentication.json.loads') as mock_json_loads:
            mock_json_loads.return_value = http_request_status_200.data

            response = passport_mixin._get_passport_access_token(parameters)

    assert response == http_request_status_200.data['access_token']


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
    mock_response.data = {"access_token": "token"}
    return mock_response


@pytest.fixture
def passport_mixin():
    passport_mixin = PassportAuthenticatingEndpointMixin
    return passport_mixin


@pytest.fixture
def parameters():
    parameters = type('', (), {})()
    parameters.client_id = "client_id"
    parameters.client_secret = "client_secret"
    parameters.grant_type = "grant_type"
    parameters.token_url = "token_url"
    return parameters