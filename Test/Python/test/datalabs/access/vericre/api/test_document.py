""" source: datalabs.access.vericre.api.profile """
from collections import namedtuple
import logging

import mock
import pytest

from datalabs.access.api.task import ResourceNotFound
from datalabs.access.vericre.api.document import ProfileDocumentsEndpointTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_query_for_documents(profile_documents_event, document_query_results):
    profile_documents_event["path"] = dict(entityId="12345678")

    with mock.patch("datalabs.access.vericre.api.document.Database"):
        session = mock.MagicMock()

        session.execute.return_value = document_query_results

        task = ProfileDocumentsEndpointTask(profile_documents_event)

        sql = task._query_for_documents(task._parameters.path.get("entityId"))

        results = session.execute(sql)

    assert (hasattr(results[0], attr) for attr in ["document_identifier", "document_name", "document_path"])
    assert len(results) == 3


# pylint: disable=redefined-outer-name, protected-access
def test_download_files_for_profile(profile_documents_event, empty_document_query_result):
    profile_documents_event["path"] = dict(entityId="12345678")
    task = ProfileDocumentsEndpointTask(profile_documents_event)

    with pytest.raises(ResourceNotFound) as except_info:
        task._download_files_for_profile(empty_document_query_result, "")

    assert except_info.type == ResourceNotFound
    assert str(except_info.value) == "No documents where found in VeriCre for the given entity ID."


@pytest.fixture
def profile_documents_event():
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
    )


@pytest.fixture
def document_query_results():
    Result = namedtuple("Result", "document_identifier document_name document_path")
    return [
        Result(
            document_identifier="Copy of current professional liability insurance face sheet",
            document_name="face sheet.pdf",
            document_path="12345678/General_Documents",
        ),
        Result(
            document_identifier="Curriculum Vitae (CV)",
            document_name="Curriculum Vitae.pdf",
            document_path="12345678/General_Documents",
        ),
        Result(document_identifier="Profile Avatar", document_name="Avatar.png", document_path="12345678/Avatar"),
    ]


@pytest.fixture
def empty_document_query_result():
    return []
