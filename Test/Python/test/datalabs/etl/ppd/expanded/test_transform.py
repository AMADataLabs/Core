""" source: datalabs.etl.ppd.expanded.transform """
import logging
import os

import mock
import pytest

from datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_data_setup_correctly(extractor_file):
    with open(extractor_file) as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_transformer_produces_two_datasets(etl):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        etl.run()

    transformer = etl.task._transformer

    LOGGER.debug('Transformed Data: %s', transformer.data)
    assert len(transformer.data) == 2


# pylint: disable=redefined-outer-name, protected-access
def test_transformer_data_has_three_data_rows(etl):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        etl.run()

    transformer = etl.task._transformer
    rows = transformer.data[0].decode().split('\n')
    LOGGER.debug('Row Data: %s', rows)

    assert len(rows) == 5  # Headers, 3 x Data, LF at end of file


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def environment(extractor_file, loader_directory):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR__TASK_CLASS'] = 'datalabs.etl.ppd.expanded.extract.LocalPPDExtractorTask'
    os.environ['EXTRACTOR__BASE_PATH'] = os.path.dirname(extractor_file)
    os.environ['EXTRACTOR__FILES'] = 'PhysicianProfessionalDataFile_*'
    os.environ['EXTRACTOR__INCLUDE_NAMES'] = 'True'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'datalabs.etl.ppd.expanded.transform.ParseToPPDTransformerTask'
    os.environ['TRANSFORMER__PARSERS'] = 'datalabs.curate.ppd.expanded.parse.ExpandedPPDParser'

    os.environ['LOADER__TASK_CLASS'] = 'datalabs.etl.load.ConsoleLoaderTask'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def etl(environment):
    task_wrapper_class = import_plugin(os.getenv('TASK_WRAPPER_CLASS'))
    task_wrapper = task_wrapper_class(parameters={})

    return task_wrapper
