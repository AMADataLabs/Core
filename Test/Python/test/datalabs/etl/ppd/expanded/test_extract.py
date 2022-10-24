""" source: datalabs.etl.ppd.expanded.extract """
import logging
import os
import pickle

import pytest

from   datalabs.etl.ppd.expanded.extract import LocalPPDExtractorTask

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
def test_extractor_data_is_reasonable(parameters):
    task = LocalPPDExtractorTask(parameters)

    output = task.run()

    LOGGER.debug('Extracted Data: %s', output)
    assert len(output) == 1

    named_files_data = pickle.loads(output[0])
    assert len(named_files_data) == 1
    _, data = zip(*named_files_data)
    assert len(data) == 1
    assert len(data[0].decode().split('\n')) == 3


@pytest.fixture
def parameters(extractor_file):
    return dict(
        BASE_PATH=os.path.dirname(extractor_file),
        FILES='PhysicianProfessionalDataFile_*',
        INCLUDE_NAMES='True'
    )
