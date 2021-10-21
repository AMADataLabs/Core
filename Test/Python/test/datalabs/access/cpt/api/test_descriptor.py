""" source: datalabs.etl.cpt.extract """
from   collections import namedtuple
from   datetime import date
import logging

import mock
import pytest

from   datalabs.access.cpt.api.descriptor import DescriptorEndpointTask
import datalabs.model.cpt.api as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_lengths_are_valid(event):
    task = DescriptorEndpointTask(event)

    assert task._lengths_are_valid(['short'])
    assert task._lengths_are_valid(['short', 'medium'])
    assert task._lengths_are_valid(['short', 'medium', 'long'])


# pylint: disable=redefined-outer-name, protected-access
def test_query_for_descriptors(event, query_results):
    with mock.patch('datalabs.access.cpt.api.descriptor.DescriptorEndpointTask._get_database'):
        session = mock.MagicMock()
        session.query.return_value.join.return_value.filter.return_value = query_results
        task = DescriptorEndpointTask(event)
        results = task._query_for_descriptors(session)

    assert all(hasattr(results, attr) for attr in ['Code', 'ShortDescriptor', 'MediumDescriptor', 'LongDescriptor'])


# pylint: disable=redefined-outer-name, protected-access
def test_generate_response_body(query_results):
    with mock.patch('datalabs.access.cpt.api.descriptor.DescriptorEndpointTask._get_database'):
        session = mock.MagicMock()
        session.query.return_value.join.return_value.all.return_value = query_results
        task = DescriptorEndpointTask(event)
        query = task._query_for_descriptors(session)
        response_body = task._generate_response_body(query.all(), ['short', 'long'], "english")

    assert type(response_body).__name__ == 'list'
    item = response_body[0]
    assert 'code' in item
    assert 'short_descriptor' in item
    assert 'medium_descriptor' not in item
    assert 'long_descriptor' in item


@pytest.fixture
def event():
    return dict(
        pathParameters=dict(code='00100'),
        multiValueQueryStringParameters=dict(
            length=['short', 'long']
        )
    )


@pytest.fixture
def context():
    return dict(function_name='descriptor')


@pytest.fixture
def expected_response_body():
    return dict(
        code='00100',
        short_descriptor='ANESTH SALIVARY GLAND',
        long_descriptor='Anesthesia for procedures on salivary glands, including biopsy'
    )


@pytest.fixture
def query_results():
    Result = namedtuple('Result', 'Code ShortDescriptor MediumDescriptor LongDescriptor')
    return [Result(
        Code=dbmodel.Code(code='00100', modified_date=date(2020, 7, 6), deleted=False),
        ShortDescriptor=dbmodel.ShortDescriptor(
            code='00100',
            descriptor='ANESTH SALIVARY GLAND',
            modified_date=date(2020, 7, 6),
            deleted=False
        ),
        MediumDescriptor=dbmodel.MediumDescriptor(
            code='00100',
            descriptor='ANESTHESIA SALIVARY GLANDS WITH BIOPSY',
            modified_date=date(2020, 7, 6),
            deleted=False
        ),
        LongDescriptor=dbmodel.LongDescriptor(
            code='00100',
            descriptor='Anesthesia for procedures on salivary glands, including biopsy',
            modified_date=date(2020, 7, 6),
            deleted=False
        )
    )]
