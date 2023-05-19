""" source: datalabs.access.vericre.api.profile """
from   collections import namedtuple
import logging

import mock
import pytest

from   datalabs.access.api.task import ResourceNotFound, InternalServerError
from   datalabs.access.vericre.api.profile import ProfileDocumentsEndpointTask, AMAProfilePDFEndpointTask, CAQHProfilePDFEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("profile_documents_event")
def test_query_for_documents(profile_documents_event, document_query_results):
    profile_documents_event["path"] = dict(entityId='12345678')

    with mock.patch('datalabs.access.vericre.api.profile.Database'):
        session = mock.MagicMock()

        session.query.return_value.union.return_value = document_query_results
        
        task = ProfileDocumentsEndpointTask(profile_documents_event)

        sub_query = task._sub_query_for_documents(session)

        results = task._query_for_documents(session, sub_query)

    assert (hasattr(results[0], attr) for attr in ['document_identifier', 'document_name', 'document_path'])
    assert len(results) == 3


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("profile_documents_event")
def test_download_files_for_profile(profile_documents_event, empty_document_query_result):
    profile_documents_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info:
        task = ProfileDocumentsEndpointTask(profile_documents_event)

        task._download_files_for_profile(empty_document_query_result, task._parameters.path.get('entityId'))

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == 'No file found for the given entity ID'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("ama_profile_pdf_event")
def test_token_response_error(ama_profile_pdf_event, http_request_status_404):
    ama_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.AMAProfilePDFEndpointTask._request_ama_token', 
            return_value = http_request_status_404
        ):
        task = AMAProfilePDFEndpointTask(ama_profile_pdf_event)

        task._get_ama_access_token()

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("ama_profile_pdf_event")
def test_assert_profile_exists_error(ama_profile_pdf_event, http_request_status_404):
    ama_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.AMAProfilePDFEndpointTask._request_ama_profile', 
            return_value = http_request_status_404
        ):
        task = AMAProfilePDFEndpointTask(ama_profile_pdf_event)

        task._assert_profile_exists(task._parameters.path.get('entityId'))

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Internal Server error caused by: {http_request_status_404.reason}, status: {http_request_status_404.status}'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("ama_profile_pdf_event")
def test_get_profile_pdf_error(ama_profile_pdf_event, http_request_status_404):
    ama_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.AMAProfilePDFEndpointTask._request_ama_profile_pdf', 
            return_value = http_request_status_404
        ):
        task = AMAProfilePDFEndpointTask(ama_profile_pdf_event)

        task._get_profile_pdf(task._parameters.path.get('entityId'))

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Internal Server error caused by: {http_request_status_404.reason}, status: {http_request_status_404.status}'


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_query_for_provider_id(caqh_profile_pdf_event, provider_id_query_results):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with mock.patch('datalabs.access.vericre.api.profile.Database'):
        session = mock.MagicMock()

        session.query.return_value.join.return_value = provider_id_query_results
        
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        results = task._query_for_provider_id(session)

    assert (hasattr(results[0], attr) for attr in ['caqh_profile_id'])
    assert len(results) == 1


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_verify_query_result_zero(caqh_profile_pdf_event, provider_id_query_result_empty):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info:
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        results = task._verify_query_result(provider_id_query_result_empty)

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == f'Provider ID from Entity ID in Vericre not found'


### query_result > 1
# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_verify_query_result_multi(caqh_profile_pdf_event, provider_id_query_result_multi):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info:
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        results = task._verify_query_result(provider_id_query_result_multi)

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Multiple records found for the given Entity ID in Vericre'


@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_fetch_caqh_pdf(caqh_profile_pdf_event, http_request_status_404):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.CAQHProfilePDFEndpointTask._request_caqh_pdf', 
            return_value = http_request_status_404
        ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._fetch_caqh_pdf('caqh-11223344')

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


### response.status != 200
@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_get_caqh_provider_id_from_npi(caqh_profile_pdf_event, http_request_status_404):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.CAQHProfilePDFEndpointTask._request_caqh_provider_id_from_npi', 
            return_value = http_request_status_404
        ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._get_caqh_provider_id_from_npi('npi-11223344')

    assert except_info.type == InternalServerError
    assert str(except_info.value) == f'Internal Server error caused by: {http_request_status_404.data}, status: {http_request_status_404.status}'


### provider_data['provider_found_flag'] != "Y"
@pytest.mark.usefixtures("caqh_profile_pdf_event")
def test_get_caqh_provider_id_from_npi_provider_found_flag(caqh_profile_pdf_event, http_request_provider_found_flag_N):
    caqh_profile_pdf_event["path"] = dict(entityId='12345678')

    with pytest.raises(Exception) as except_info, \
        mock.patch(
            'datalabs.access.vericre.api.profile.CAQHProfilePDFEndpointTask._request_caqh_provider_id_from_npi', 
            return_value = http_request_provider_found_flag_N
        ):
        task = CAQHProfilePDFEndpointTask(caqh_profile_pdf_event)

        task._get_caqh_provider_id_from_npi('npi-11223344')

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == f'CAQH Provider ID from NPI ID in CAQH ProView not found'


@pytest.fixture
def document_query_results():
    Result = namedtuple('Result', 'document_identifier document_name document_path')
    return [
        Result(
            document_identifier = 'Copy of current professional liability insurance face sheet',
            document_name = 'face sheet.pdf',
            document_path = '12345678/General_Documents'
        ),
        Result(
            document_identifier = 'Curriculum Vitae (CV)',
            document_name = 'Curriculum Vitae.pdf',
            document_path = '12345678/General_Documents'
        ),
        Result(
            document_identifier = 'Profile Avatar',
            document_name = 'Avatar.png',
            document_path = '12345678/Avatar'
        )
    ]

@pytest.fixture
def empty_document_query_result():
    return []

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
    Result = namedtuple('Result', 'caqh_profile_id')

    return [
        Result(
            caqh_profile_id = 'npi-11223344'
        )
    ]

@pytest.fixture
def provider_id_query_result_empty():
    return []

@pytest.fixture
def provider_id_query_result_multi():
    Result = namedtuple('Result', 'caqh_profile_id')

    return [
        Result(
            caqh_profile_id = 'npi-11223344'
        ),
        Result(
            caqh_profile_id = '12341234'
        )
    ]

@pytest.fixture
def http_request_provider_found_flag_N():
    response_data = '{"provider_found_flag": "N"}'
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.data = response_data
    
    return mock_response