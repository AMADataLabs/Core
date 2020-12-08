""" source: datalabs.access.awslambda """
import json
import os

import mock
import pytest

from   datalabs.access.api.awslambda import APIEndpointTaskWrapper
import datalabs.access.api.task as api


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
        parameters = wrapper._get_task_parameters()

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
    response = wrapper._handle_exception(api.APIEndpointException('failed'))

    assert response['statusCode'] == 400
    assert response['body'] == json.dumps(dict(message='failed'))


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_generate_response(event):
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        wrapper = APIEndpointTaskWrapper(MockTask, parameters=event)
        wrapper.run()
        response = wrapper._generate_response()

    assert response['statusCode'] == 200
    assert response['body'] == json.dumps(dict())


class MockTask(api.APIEndpointTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return api.APIEndpointParameters(
        path=dict(foo='bar'),
        query=dict(ping='pong'),
        database=dict(
            name='name', backend='postgresql+psycopg2', host='host', port='5432', username='username', password='password'
        ),
        bucket=dict(name='mybucket', base_path='AMA/SOMETHING', url_duration='30')
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['DATABASE_HOST'] = 'host'
    os.environ['DATABASE_SECRET'] = '{"username":"username", "password":"password", "port":5432, ' \
                                             '"dbname":"name", "engine": "postgres"}'
    os.environ['BUCKET_NAME'] = 'mybucket'
    os.environ['BUCKET_BASE_PATH'] = 'AMA/SOMETHING'
    os.environ['BUCKET_URL_DURATION'] = '30'

    yield dict(
        pathParameters=dict(foo='bar'),
        queryStringParameters=dict(ping='pong'),
    )

    os.environ.clear()
    os.environ.update(current_env)
