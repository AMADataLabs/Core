""" source: datalabs.access.vericre.monitor """
import  json

import  pytest
import  mock

from    datalabs.access.vericre.api.monitor import MonitorNotificationsEndpointTask, MonitorProfilesEndpointTask
from    Test.Python.test.datalabs.access.vericre.api import constants


# # pylint: disable=redefined-outer-name, protected-access
def test_get_notifications(monitor_notifications_params, get_notification_response):
    with mock.patch(
            "datalabs.access.vericre.api.authentication.EProfilesAuthenticatingEndpointMixin."
            "_authenticate_to_eprofiles",
            return_value="token"
    ), mock.patch(
        'datalabs.access.vericre.api.monitor.MonitorNotificationsEndpointTask._request_notifications',
        return_value=get_notification_response
    ):
        task = MonitorNotificationsEndpointTask(monitor_notifications_params)
        task.run()

    expected_json = json.loads(constants.SAMPLE_NOTIFICATION_JSON)
    task_response = json.dumps(task._response_body)

    assert expected_json == json.loads(task_response)


# # pylint: disable=redefined-outer-name, protected-access
def test_get_profile_monitors(monitor_profiles_params, get_profiles_response):
    with mock.patch(
            "datalabs.access.vericre.api.authentication.EProfilesAuthenticatingEndpointMixin."
            "_authenticate_to_eprofiles",
            return_value="token"
    ), mock.patch(
        'datalabs.access.vericre.api.monitor.MonitorProfilesEndpointTask._get_profile_monitors',
        return_value=get_profiles_response
    ):
        task = MonitorProfilesEndpointTask(monitor_profiles_params)
        task.run()

    expected_json = json.loads(constants.SAMPLE_MONITOR_JSON)
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
def get_profiles_response():
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = constants.SAMPLE_MONITOR_XML.encode("utf-8")
    mock_response.decode.return_value = constants.SAMPLE_MONITOR_XML
    return mock_response


@pytest.fixture
def monitor_notifications_params():
    return dict(
        path={},
        query={},
        client_id='',
        client_secret='',
        token_url='',
        monitor_notification_url='',
        method=''
    )


@pytest.fixture
def monitor_profiles_params():
    return dict(
        path={},
        query={},
        client_id='',
        client_secret='',
        token_url='',
        monitor_profile_url='',
        method=''
    )
