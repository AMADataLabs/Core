""" REPLACE WITH DOCSTRING """
import os
import pytest

from   datalabs.access.awslambda import APIEndpointTaskWrapper, APIEndpointException
from   datalabs.access.task import APIEndpointTask, APIEndpointParameters


def test_task_wrapper_get_task_parameters(expected_parameters, event):
    wrapper = APIEndpointTaskWrapper(dict())
    parameters = wrapper._get_task_parameters(event)

    assert expected_parameters == parameters


def test_task_wrapper_handle_exception():
    wrapper = APIEndpointTaskWrapper(dict())
    status_code, body = wrapper._handle_exception(APIEndpointException('failed'))

    assert status_code == 400
    assert body == dict(message='failed')


def test_task_wrapper_generate_response():
    wrapper = APIEndpointTaskWrapper(dict())
    task = MockTask(None)
    status_code, body = wrapper._generate_response(task)

    assert status_code == 200
    assert body == dict()


class MockTask(APIEndpointTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return APIEndpointParameters(
        path=dict(foo='bar'),
        query=dict(ping='pong'),
        database=dict(name='name', backend='backend', host='host', username='username', password='password')
    )


@pytest.fixture
def event():
    current_env = os.environ
    current_env['DATABASE_NAME'] = 'name'
    current_env['DATABASE_BACKEND'] = 'backend'
    current_env['DATABASE_HOST'] = 'host'
    current_env['DATABASE_USERNAME'] = 'username'
    current_env['DATABASE_PASSWORD'] = 'password'

    yield dict(
        pathParameters=dict(foo='bar'),
        queryStringParameters=dict(ping='pong'),
    )

    os.environ = current_env
