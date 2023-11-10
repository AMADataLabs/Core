""" source: datalabs.access.vericre.api.profile """
import logging

import mock
import pytest

from datalabs.access.api.task import ResourceNotFound
from datalabs.access.vericre.api.pdf import AMAProfilePDFEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_assert_profile_exists_error(ama_profile_pdf_event, http_request_status_404):
    ama_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info, mock.patch(
        "datalabs.access.vericre.api.pdf.AMAProfilePDFEndpointTask._request_ama_profile",
        return_value=http_request_status_404,
    ):
        task = AMAProfilePDFEndpointTask(ama_profile_pdf_event)

        task._assert_profile_exists(task._parameters.path.get("entityId"))

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == "An AMA eProfiles profile was not found for the provided entity ID."


# pylint: disable=redefined-outer-name, protected-access
def test_get_profile_pdf_error(ama_profile_pdf_event, http_request_status_404):
    ama_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info, mock.patch(
        "datalabs.access.vericre.api.pdf.AMAProfilePDFEndpointTask._request_ama_profile_pdf",
        return_value=http_request_status_404,
    ):
        task = AMAProfilePDFEndpointTask(ama_profile_pdf_event)

        task._get_profile_pdf(task._parameters.path.get("entityId"))

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == "An AMA eProfiles profile was not found for the provided entity ID."


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
def ama_profile_pdf_event():
    return dict(
        path={},
        query={},
        authorization={},
        identity={},
        database_host="",
        database_port="",
        database_backend="",
        database_name="",
        database_username="",
        database_password="",
        document_bucket="",
        client_id="",
        client_secret="",
        token_url="",
        profile_url="",
        pdf_url="",
    )
