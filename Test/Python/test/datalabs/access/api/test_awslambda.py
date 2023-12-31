""" source: datalabs.access.awslambda """
import base64
import json
import os

import mock
import pytest

from   datalabs.access.api.awslambda import APIEndpointTaskWrapper
import datalabs.access.api.task as api


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event, get_dag_task_parameters_from_dynamodb):
    wrapper = APIEndpointTaskWrapper(parameters=event)

    with mock.patch.object(
        APIEndpointTaskWrapper,
        '_get_dag_task_parameters_from_dynamodb',
        new=get_dag_task_parameters_from_dynamodb
    ):
        wrapper._setup_environment()
        parameters = wrapper._get_task_parameters()

    for key, value in expected_parameters.items():
        assert key in parameters
        assert value == parameters[key]


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = APIEndpointTaskWrapper(parameters=event)
    response = wrapper._handle_exception(api.APIEndpointException('failed'))

    assert response['statusCode'] == 400
    assert response['body'] == json.dumps(dict(message='failed'))


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_success(event, get_dag_task_parameters_from_dynamodb):
    with mock.patch.object(
        APIEndpointTaskWrapper,
        '_get_dag_task_parameters_from_dynamodb',
        new=get_dag_task_parameters_from_dynamodb
    ):
        wrapper = APIEndpointTaskWrapper(parameters=event)
        wrapper.run()
        response = wrapper._handle_success()

    assert response['statusCode'] == 200
    assert response['body'] == json.dumps({})


# pylint: disable=redefined-outer-name, protected-access
def test_get_payload_returns_correct_json(encoded_payload):
    payload = APIEndpointTaskWrapper._get_payload(encoded_payload, "application/json")

    assert len(payload) == 1
    assert "message" in payload
    assert payload["message"] == "Hello!"


# pylint: disable=redefined-outer-name, protected-access
def test_get_empty_payload_returns_none():
    payload = APIEndpointTaskWrapper._get_payload(None, "application/json")

    assert payload is None


class MockTask(api.APIEndpointTask):
    def run(self):
        pass


@pytest.fixture
def task_parameters():
    return dict(
        TASK_CLASS='test.datalabs.access.api.test_awslambda.MockTask',
        DATABASE_NAME='name',
        DATABASE_BACKEND='postgresql+psycopg2',
        DATABASE_HOST='host',
        DATABASE_PORT='5432',
        DATABASE_USERNAME='username',
        DATABASE_PASSWORD='password',
        BUCKET_NAME='mybucket',
        BUCKET_BASE_PATH='AMA/SOMETHING',
        BUCKET_URL_DURATION='30'
    )


@pytest.fixture
def get_dag_task_parameters_from_dynamodb(task_parameters):
    # pylint: disable=unused-argument
    def _get_dag_task_parameters_from_dynamodb(cls, dag, task, execution_time=None):
        parameters = {}

        if task == "ROUTE":
            parameters = dict(TEST_ENDPOINT="/test")
        elif task == "TEST_ENDPOINT":
            parameters = task_parameters

        return parameters

    return _get_dag_task_parameters_from_dynamodb


@pytest.fixture
def expected_parameters(task_parameters):
    parameters = dict(
        method="GET",
        path=dict(foo='bar'),
        query=dict(ping='pong'),
        authorization=dict(
            user_id="000002164389",
            user_name="TEST Health Solutions",
            authorizations=dict(
                CPTAPI={"start": "2020-01-01-05:00", "end": "2048-10-06-05:00"}
            )
        ),
        identity=dict(
            cognitoIdentityPoolId=None,
            cognitoIdentityId=None,
            vpceId="vpce-0bc731de06c089ce1",
            principalOrgId=None,
            cognitoAuthenticationType=None,
            userArn=None,
            userAgent="PostmanRuntime/7.29.0",
            accountId=None,
            caller=None,
            sourceIp="172.31.10.211",
            accessKey=None,
            vpcId="vpc-0f54b51b973b709d2",
            cognitoAuthenticationProvider=None,
            user=None
        ),
        payload=None
    )

    parameters.update(task_parameters)

    return parameters


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ.clear()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.access.api.awslambda.APIEndpointTaskWrapper'
    os.environ['DYNAMODB_CONFIG_TABLE'] = 'DataLake-configuration-nas'
    os.environ['API_ID'] = 'TEST_API'

    endpoint = "/test"
    single_query_parameters = dict(ping='pong')
    multi_query_parameters = {}

    yield json.loads(
        f'''{{
            "resource": "{endpoint}",
            "path": "{endpoint}",
            "httpMethod": "GET",
            "headers": {{
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate, br",
                "Authorization": "Bearer WJfefqn5pWUZ9jv2RorEucE0MLVUemayqGAByOsS",
                "Host": "localhost",
                "Postman-Token": "50934e08-9798-4eb4-bf8d-ec8e96060a2a",
                "User-Agent": "PostmanRuntime/7.29.0",
                "x-amzn-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
                "x-amzn-tls-version": "TLSv1.2",
                "x-amzn-vpc-id": "vpc-0f54b51b973b709d2",
                "x-amzn-vpce-config": "1",
                "x-amzn-vpce-id": "vpce-0bc731de06c089ce1",
                "X-Forwarded-For": "172.31.10.211"
            }},
            "multiValueHeaders": {{
                "Accept": ["*/*"],
                "Accept-Encoding": ["gzip, deflate, br"],
                "Authorization": ["Bearer WJfefqn5pWUZ9jv2RorEucE0MLVUemayqGAByOsS"],
                "Host": ["localhost"],
                "Postman-Token": ["50934e08-9798-4eb4-bf8d-ec8e96060a2a"],
                "User-Agent": ["PostmanRuntime/7.29.0"],
                "x-amzn-cipher-suite": ["ECDHE-RSA-AES128-GCM-SHA256"],
                "x-amzn-tls-version": ["TLSv1.2"],
                "x-amzn-vpc-id": ["vpc-0f54b51b973b709d2"],
                "x-amzn-vpce-config": ["1"],
                "x-amzn-vpce-id": ["vpce-0bc731de06c089ce1"],
                "X-Forwarded-For": ["172.31.10.211"]
            }},
            "queryStringParameters": {json.dumps(single_query_parameters)},
            "multiValueQueryStringParameters": {json.dumps(multi_query_parameters)},
            "pathParameters": {{"foo": "bar"}},
            "stageVariables": null,
            "requestContext": {{
                "resourceId": "zs07zi",
                "authorizer": {{
                    "CPTAPI": "{{\\"start\\":\\"2020-01-01-05:00\\",\\"end\\":\\"2048-10-06-05:00\\"}}",
                    "principalId": "username",
                    "integrationLatency": 0,
                    "customerNumber": "000002164389",
                    "customerName": "TEST Health Solutions"
                }},
                "resourcePath": "{endpoint}",
                "operationName": "getFiles",
                "httpMethod": "{endpoint}",
                "extendedRequestId": "QmOw7G1BIAMFYJQ=",
                "requestTime": "15/Apr/2022:01:05:22 +0000",
                "path": "{endpoint}",
                "accountId": "644454719059",
                "protocol": "HTTP/1.1",
                "stage": "sbx",
                "domainPrefix": "cpt-api-sbx",
                "requestTimeEpoch": 1649984722561,
                "requestId": "c2fc2e4d-8082-4375-a923-e7c4fddbf51a",
                "identity": {{
                    "cognitoIdentityPoolId": null,
                    "cognitoIdentityId": null,
                    "vpceId": "vpce-0bc731de06c089ce1",
                    "principalOrgId": null,
                    "cognitoAuthenticationType": null,
                    "userArn": null,
                    "userAgent": "PostmanRuntime/7.29.0",
                    "accountId": null,
                    "caller": null,
                    "sourceIp": "172.31.10.211",
                    "accessKey": null,
                    "vpcId": "vpc-0f54b51b973b709d2",
                    "cognitoAuthenticationProvider": null,
                    "user": null
                }},
                "domainName": "localhost",
                "apiId": "b1secmwhmj"
            }},
            "body": null,
            "isBase64Encoded": false
        }}'''
    )

    os.environ.clear()
    os.environ.update(current_env)


@pytest.fixture
def encoded_payload():
    return base64.b64encode('{"message":"Hello!"}'.encode())
