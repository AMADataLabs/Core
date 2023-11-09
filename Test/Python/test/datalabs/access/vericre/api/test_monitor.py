""" source: datalabs.access.vericre.monitor """
import  json

import  pytest
import  mock

from    Test.Python.test.datalabs.access.vericre.api import constants
from    datalabs.access.vericre.api.monitor import MonitorNotificationsEndpointTask, MonitorEntitiesEndpointTask


def test_get_notifications(notification_event, get_notification_response):
    with mock.patch(
            'datalabs.access.vericre.api.authentication.PassportAuthenticatingEndpointMixin._get_passport_access_token',
            return_value="token"
    ), mock.patch(
        'datalabs.access.vericre.api.monitor.MonitorNotificationsEndpointTask._request_notifications',
        return_value=get_notification_response
    ):
        task = MonitorNotificationsEndpointTask(notification_event)
        task.run()

    expected_json = json.loads(constants.SAMPLE_NOTIFICATION_JSON)
    task_response = json.dumps(task._response_body)

    assert expected_json == json.loads(task_response)


def test_get_entities(entity_event, get_entity_response):
    with mock.patch(
            'datalabs.access.vericre.api.authentication.PassportAuthenticatingEndpointMixin._get_passport_access_token',
            return_value="token"
    ), mock.patch(
        'datalabs.access.vericre.api.monitor.MonitorEntitiesEndpointTask._get_entities',
        return_value=get_entity_response
    ):
        task = MonitorEntitiesEndpointTask(entity_event)
        task.run()

    expected_json = json.loads(constants.SAMPLE_ENTITY_JSON)
    task_response = json.dumps(task._response_body)

    assert expected_json == json.loads(task_response)


@pytest.fixture
def get_notification_response():
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = constants.SAMPLE_NOTIFICATION_XML.encode("utf-8")
    mock_response.decode.return_value = constants.SAMPLE_NOTIFICATION_XML
    return mock_response


@pytest.fixture
def get_entity_response():
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = constants.SAMPLE_ENTITY_XML.encode("utf-8")
    mock_response.decode.return_value = constants.SAMPLE_ENTITY_XML
    return mock_response


@pytest.fixture
def notification_event():
    return dict(
        path={},
        query={},
        client_id='',
        client_secret='',
        token_url='',
        notification_url='',
        method=''
    )


@pytest.fixture
def entity_event():
    return dict(
        path={},
        query={},
        client_id='',
        client_secret='',
        token_url='',
        entity_url='',
        method=''
    )
