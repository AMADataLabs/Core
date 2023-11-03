""" source: datalabs.access.api.task """
import pytest
import mock

import datalabs.access.api.task as api


# pylint: disable=abstract-method
class BadTask(api.APIEndpointTask):
    pass


# pylint: disable=protected-access
class GoodTask(api.APIEndpointTask):
    # pylint: disable=unused-argument
    def run(self):
        GoodTask.run.called = True


GoodTask.run.called = False  # pylint: disable=protected-access


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


# pylint: disable=protected-access
def test_task_is_not_abstract():
    GoodTask(None).run()


def test_api_endpoint_exceptions_have_status_and_message():
    exception = api.APIEndpointException('failed', -1)

    assert exception.status_code == -1
    assert exception.message == 'failed'


def test_default_api_endpoint_exception_status_code_is_400():
    exception = api.APIEndpointException('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_invalid_request_status_is_400():
    exception = api.InvalidRequest('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_resource_not_found_is_404():
    exception = api.ResourceNotFound('failed')

    assert exception.status_code == 404
    assert exception.message == 'failed'


# pylint: disable=redefined-outer-name, protected-access
def test_token_response_error(passport_mixin, parameters, http_request_status_404, self=None):
    with mock.patch(
            'datalabs.access.api.task.PassportAuthenticatingEndpointMixin._request_ama_token',
            return_value=http_request_status_404
    ), pytest.raises(Exception) as except_info:
        passport_mixin._get_passport_access_token(parameters)

    assert except_info.type == api.InternalServerError
    assert str(except_info.value) == \
           f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


def test_get_token(passport_mixin, http_request_status_200, parameters, self=None):
    with mock.patch(
            'datalabs.access.api.task.PassportAuthenticatingEndpointMixin._request_ama_token',
            return_value=http_request_status_200
    ):
        with mock.patch('datalabs.access.api.task.json.loads') as mock_json_loads:
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
    passport_mixin = api.PassportAuthenticatingEndpointMixin
    return passport_mixin


@pytest.fixture
def parameters():
    parameters = type('', (), {})()
    parameters.client_id = "client_id"
    parameters.client_secret = "client_secret"
    parameters.grant_type = "grant_type"
    parameters.token_url = "token_url"
    return parameters
