""" source: datalabs.access.awslambda """
import json
import os

import mock
import pytest

from   datalabs.access.api.awslambda import APIEndpointTaskWrapper
import datalabs.access.api.task as api


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = APIEndpointTaskWrapper(parameters=event)
            wrapper._setup_environment()
            parameters = wrapper._get_task_parameters()

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = APIEndpointTaskWrapper(parameters=event)
    response = wrapper._handle_exception(api.APIEndpointException('failed'))

    assert response['statusCode'] == 400
    assert response['body'] == json.dumps(dict(message='failed'))


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_success(event):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = APIEndpointTaskWrapper(parameters=event)
            wrapper.run()
            response = wrapper._handle_success()

    assert response['statusCode'] == 200
    assert response['body'] == json.dumps(dict())


class MockTask(api.APIEndpointTask):
    def _run(self, database):
        pass


@pytest.fixture
def expected_parameters():
    return dict(
        path=dict(foo='bar'),
        query=dict(ping='pong'),
        authorization=dict(
            user_id="000002164389",
            user_name="TEST Health Solutions",
            authorizations=dict(
                CPTAPI="2022-10-06-05:00"
            )
        ),
        database_name='name',
        database_backend='postgresql+psycopg2',
        database_host='host',
        database_port='5432',
        database_username='username',
        database_password='password',
        bucket_name='mybucket',
        bucket_base_path='AMA/SOMETHING',
        bucket_url_duration='30'
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ.clear()

    os.environ['TASK_CLASS'] = 'test.datalabs.access.api.test_awslambda.MockTask'
    os.environ['DATABASE_HOST'] = 'host'
    os.environ['DATABASE_PORT'] = '5432'
    os.environ['DATABASE_BACKEND'] = 'postgresql+psycopg2'
    os.environ['DATABASE_NAME'] = 'name'
    os.environ['DATABASE_USERNAME'] = 'username'
    os.environ['DATABASE_PASSWORD'] = 'password'
    os.environ['BUCKET_NAME'] = 'mybucket'
    os.environ['BUCKET_BASE_PATH'] = 'AMA/SOMETHING'
    os.environ['BUCKET_URL_DURATION'] = '30'

    yield dict(
        pathParameters=dict(foo='bar'),
        queryStringParameters=dict(ping='pong'),
        multiValueQueryStringParameters=None,
        requestContext=dict(
            resourceId="jnokm4",
            authorizer=dict(
                principalId="username",
                integrationLatency=4036,
                customerNumber="000002164389",
                customerName="TEST Health Solutions",
                CPTAPI="2022-10-06-05:00"
            )
        )
    )

    os.environ.clear()
    os.environ.update(current_env)
