""" source: datalabs.etl.ppd.expanded.transform """
import logging

import pytest

from datalabs.etl.ppd.expanded.transform import ParseToPPDTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_data_setup_correctly(extractor_file):
    with open(extractor_file, encoding="utf-8") as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_transformer_produces_two_datasets(parameters, ppd_data):
    task = ParseToPPDTransformerTask(parameters, [ppd_data])

    output = task.run()

    LOGGER.debug('Transformed Data: %s', output)
    assert len(output) == 2


# pylint: disable=redefined-outer-name, protected-access
def test_transformer_data_has_three_data_rows(parameters, ppd_data):
    task = ParseToPPDTransformerTask(parameters, [ppd_data])

    output = task.run()

    rows = output[0].decode().split('\n')
    LOGGER.debug('Row Data: %s', rows)

    assert len(rows) == 5  # Headers, 3 x Data, LF at end of file


@pytest.fixture
def parameters():
    return dict(
        PARSERS='datalabs.curate.ppd.expanded.parse.ExpandedPPDParser'
    )
