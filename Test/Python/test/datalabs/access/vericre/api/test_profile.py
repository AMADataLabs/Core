""" source: datalabs.access.vericre.api.profile """
from   collections import namedtuple
from   datetime import date
import logging

import mock
import pytest

from   datalabs.access.vericre.api.profile import ProfileDocumentsEndpointTask
import datalabs.model.vericre.api as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.usefixtures("event")
def test_query_for_documents(event, query_results):
    event["path"] = dict(entityId='12345678')

    with mock.patch('datalabs.access.vericre.api.profile.Database'):
        session = mock.MagicMock()
        session.query.return_value.join.return_value.filter.return_value = query_results
        task = ProfileDocumentsEndpointTask(event)
        results = task._query_for_documents(session)

    assert all(hasattr(results, attr) for attr in ['document_identifier', 'document_name', 'document_path'])


@pytest.fixture
def context():
    return dict(function_name='profile')


@pytest.fixture
def query_results():
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