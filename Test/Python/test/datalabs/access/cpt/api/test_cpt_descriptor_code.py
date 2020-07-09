""" source: datalabs.etl.cpt.extract """
from   collections import namedtuple
from   datetime import date
import json
import logging

import mock
import pytest

from   datalabs.access.cpt.api.cpt_descriptor_code import DescriptorEndpointTask
import datalabs.etl.cpt.dbmodel as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_lengths_are_valid(event):
    task = DescriptorEndpointTask(event)

    assert task._lengths_are_valid(['short']) == True
    assert task._lengths_are_valid(['short', 'medium']) == True
    assert task._lengths_are_valid(['short', 'medium', 'long']) == True


def test_query_for_descriptor(event, query_results):
    with mock.patch('datalabs.access.cpt.api.cpt_descriptor_code.DescriptorEndpointTask._get_database') as get_database:
        session = mock.MagicMock()
        session.query.return_value.join.return_value.filter.return_value = query_results
        task = DescriptorEndpointTask(event)
        results = task._query_for_descriptor(session, '00100')

    assert all(hasattr(results, attr) for attr in ['Code', 'ShortDescriptor', 'MediumDescriptor', 'LongDescriptor'])


def test_generate_response_body(query_results):
    with mock.patch('datalabs.access.cpt.api.cpt_descriptor_code.DescriptorEndpointTask._get_database') as get_database:
        session = mock.MagicMock()
        session.query.return_value.join.return_value.filter.return_value = query_results
        task = DescriptorEndpointTask(event)
        results = task._query_for_descriptor(session, '00100')
        response_body = task._generate_response_body(results, ['short', 'long'])

    assert 'code' in response_body
    assert 'short_descriptor' in response_body
    assert 'medium_descriptor' not in response_body
    assert 'long_descriptor' in response_body


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
    return dict(function_name='cpt_descriptor_code')


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
    return Result(
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
    )
