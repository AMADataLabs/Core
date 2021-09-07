""" source: datalabs.etl.s3.extract """
from   io import BytesIO
import os
import os.path
import mock
import pytest

from   botocore.response import StreamingBody
import pandas

import datalabs.etl.s3.extract as s3


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):
    with mock.patch('boto3.client'):
        task = s3.S3FileExtractorTask(parameters)

        assert isinstance(task._parameters, s3.S3FileExtractorParameters)


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('boto3.client'):
        task = s3.S3FileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/19000101/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_disabling_datestamp_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        task = s3.S3FileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_base_path_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['BASE_PATH'] = 'dir1/%Y%m%d/dir2/dir3'
        task = s3.S3FileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/19000101/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_file_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['FILES'] = 'this_one.csv,that_one.csv,\n       the_other_%Y%m%d_one.csv     '
        task = s3.S3FileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/dir2/dir3/the_other_19000101_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_caching_data_to_disk(body, parameters):
    task = s3.S3FileExtractorTask(parameters)

    path = task._cache_data_to_disk(body)

    assert os.path.isfile(path)

    data = pandas.read_csv(path)

    assert data.columns.to_list() == ['name', 'id']
    assert len(data) == 3

    os.remove(path)


def test_cp1252_decoding(parameters):
    task = s3.S3WindowsTextFileExtractorTask(parameters)
    cp1252_encoded_text = '¥'.encode('cp1252')
    unicode_encoded_text = task._decode_data(cp1252_encoded_text)

    assert unicode_encoded_text == '¥'.encode("utf-8")


@pytest.fixture
def parameters():
    return dict(
        ENDPOINT_URL='https://bogus.host.fqdn/path/file',
        ACCESS_KEY='nviowaj4902hfisafh9402fdni0ph8',
        SECRET_KEY='wr9e0afe90afohf90aw',
        REGION_NAME='us-east-42',
        BUCKET='jumanji',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )

@pytest.fixture
def body():
    data = \
b'''name,id
foo,12345
bar,54321
ping,24680
'''

    return StreamingBody(BytesIO(data), len(data))
