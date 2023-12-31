""" source: datalabs.access.vericre.api.profile """
from collections import namedtuple
import logging

import mock
import pytest

from datalabs.access.api.task import ResourceNotFound, InternalServerError
from datalabs.access.vericre.api.caqh import CAQHProfilePDFEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_query_for_provider_id(caqh_profile_pdf_event, provider_id_query_results):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with mock.patch("datalabs.access.vericre.api.caqh.Database"):
        session = mock.MagicMock()

        session.execute.return_value = provider_id_query_results

        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        sql = task._query_for_provider_id(task._parameters.path.get("entityId"))

        results = session.execute(sql)

    assert (hasattr(results[0], attr) for attr in ["caqh_profile_id"])
    assert len(results) == 1


# pylint: disable=redefined-outer-name, protected-access
def test_verify_query_result_zero(caqh_profile_pdf_event, provider_id_query_result_empty):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info:
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._verify_query_result(provider_id_query_result_empty)

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == "A provider ID was not found in VeriCre for the given entity ID."


# pylint: disable=redefined-outer-name, protected-access
def test_verify_multi_query_returns_multiple_results(caqh_profile_pdf_event, provider_id_query_result_multi):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info:
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._verify_query_result(provider_id_query_result_multi)

    assert except_info.type == InternalServerError
    assert str(except_info.value) == "Multiple records were found in VeriCre for the given entity ID."


def test_fetch_caqh_pdf(caqh_profile_pdf_event, http_request_status_404):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info, mock.patch(
        "datalabs.access.vericre.api.caqh.CAQHProfilePDFEndpointTask._request_caqh_pdf",
        return_value=http_request_status_404,
    ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._fetch_caqh_pdf("caqh-11223344")

    assert except_info.type == InternalServerError
    assert (
        str(except_info.value)
        == f"Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}"
    )


def test_get_caqh_provider_id_from_bad_npi_returns_internal_server_error(
    caqh_profile_pdf_event, http_request_status_404
):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info, mock.patch(
        "datalabs.access.vericre.api.caqh.CAQHProfilePDFEndpointTask._request_caqh_provider_id_from_npi",
        return_value=http_request_status_404,
    ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._get_caqh_provider_id_from_npi("npi-11223344")

    assert except_info.type == InternalServerError
    assert (
        str(except_info.value)
        == f"Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}"
    )


def test_get_caqh_provider_id_from_npi_returns_false_provider_found_flag(
    caqh_profile_pdf_event, http_request_provider_found_flag_n
):
    caqh_profile_pdf_event["path"] = dict(entityId="12345678")

    with pytest.raises(Exception) as except_info, mock.patch(
        "datalabs.access.vericre.api.caqh.CAQHProfilePDFEndpointTask._request_caqh_provider_id_from_npi",
        return_value=http_request_provider_found_flag_n,
    ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._get_caqh_provider_id_from_npi("npi-11223344")

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == "A provider ID was not found in CAQH ProView for the given NPI."


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
def provider_id_query_results():
    Result = namedtuple("Result", "caqh_profile_id")

    return [Result(caqh_profile_id="npi-11223344")]


@pytest.fixture
def provider_id_query_result_empty():
    return []


@pytest.fixture
def provider_id_query_result_multi():
    Result = namedtuple("Result", "caqh_profile_id")

    return [Result(caqh_profile_id="npi-11223344"), Result(caqh_profile_id="12341234")]


@pytest.fixture
def caqh_profile_pdf_event():
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
        username="",
        password="",
        org_id="",
        application_type="",
        domain="",
        provider_docs_url="",
        status_check_url="",
    )


@pytest.fixture
def http_request_provider_found_flag_n():
    response_data = '{"provider_found_flag": "N"}'
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = response_data

    return mock_response
