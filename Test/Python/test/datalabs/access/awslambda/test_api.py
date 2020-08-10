""" source: datalabs.access.awslambda """
import os
import pytest

from   datalabs.access.awslambda.api import APIEndpointTaskWrapper
import datalabs.access.task.api as api


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
    parameters = wrapper._get_task_parameters()

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
    status_code, headers, body = wrapper._handle_exception(api.APIEndpointException('failed'))

    assert status_code == 400
    assert body == dict(message='failed')


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_generate_response(event):
    wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
    wrapper.run()
    status_code, headers, body = wrapper._generate_response()

    assert status_code == 200
    assert body == dict()


class MockTask(api.APIEndpointTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return api.APIEndpointParameters(
        path=dict(foo='bar'),
        query=dict(ping='pong'),
        database=dict(
            name='name', backend='postgresql+psycopg2', host='host', username='username', password='password'
        ),
        bucket=dict(name='mybucket', base_path='AMA/SOMETHING', url_duration='30')
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['DATABASE_NAME'] = 'name'
    os.environ['DATABASE_BACKEND'] = 'postgresql+psycopg2'
    os.environ['DATABASE_HOST'] = 'host'
    os.environ['DATABASE_USERNAME'] = 'username'
    os.environ['DATABASE_PASSWORD'] = 'password'
    os.environ['BUCKET_NAME'] = 'mybucket'
    os.environ['BUCKET_BASE_PATH'] = 'AMA/SOMETHING'
    os.environ['BUCKET_URL_DURATION'] = '30'

    yield dict(
        pathParameters=dict(foo='bar'),
        queryStringParameters=dict(ping='pong'),
    )

    os.environ.clear()
    os.environ.update(current_env)
