""" source: datalabs.etl.fs.extract """
import logging
import os

import pytest

from   datalabs.etl.fs.extract import LocalFileExtractorTask, LocalWindowsTextFileExtractorTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_data_setup_correctly(extractor_file):
    with open(extractor_file, encoding="utf-8") as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_extractor_loads_correct_file(extractor_file):
    parameters = dict(BASE_PATH=os.path.dirname(extractor_file), FILES='PhysicianProfessionalDataFile_*')

    task = LocalFileExtractorTask(parameters)

    output = task.run()

    assert len(output) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    task = LocalFileExtractorTask(parameters)

    files = task._get_files()

    assert len(files) == 3
    assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


def test_cp1252_decoding(parameters):
    task = LocalWindowsTextFileExtractorTask(parameters)
    cp1252_encoded_text = '¥'.encode('cp1252')
    unicode_encoded_text = task._decode_data(cp1252_encoded_text)

    assert unicode_encoded_text == '¥'.encode("utf-8")


@pytest.fixture
def parameters():
    return dict(
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )
