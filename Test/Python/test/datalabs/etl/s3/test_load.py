""" source: datalabs.etl.s3.extract """
import pytest
import tempfile

import mock

import pandas

import datalabs.etl.s3.load as s3


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):
    with mock.patch('boto3.client'):
        task = s3.S3FileLoaderTask(parameters)

        assert isinstance(task._parameters, s3.S3FileLoaderParameters)


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('boto3.client'):
        task = s3.S3FileLoaderTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/19000101/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_disabling_datestamp_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        task = s3.S3FileLoaderTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_base_path_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['BASE_PATH'] = 'dir1/%Y%m%d/dir2/dir3'
        task = s3.S3FileLoaderTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/19000101/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_file_works(parameters):
    with mock.patch('boto3.client'):
        parameters['INCLUDE_DATESTAMP'] = 'false'
        parameters['FILES'] = 'this_one.csv,that_one.csv,\n     the_%Y%m%d_other_one.csv    '
        task = s3.S3FileLoaderTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/dir2/dir3/the_19000101_other_one.csv'

# pylint: disable=redefined-outer-name, protected-access
def test_loading_data_from_a_file(data_file, parameters):
    parameters["ON_DISK"] = 'True'
    task = s3.S3FileLoaderTask(parameters)
    task._client = mock.Mock()

    task._load_file(data_file.encode(), 'ACME/Stuff/something.csv')

    cache_file = task._client.put_object.call_args[1]["Body"]

    assert hasattr(cache_file, "read")


# pylint: disable=redefined-outer-name, protected-access
def test_cp1252_encoding(parameters):
    task = s3.S3WindowsTextFileLoaderTask(parameters)
    unicode_encoded_text = '¥'.encode('utf-8')
    cp1252_encoded_text = task._encode_data(unicode_encoded_text)

    assert cp1252_encoded_text == '¥'.encode('cp1252')


@pytest.fixture
def parameters():
    return dict(
        ENDPOINT_URL='https://bogus.host.fqdn/path/file',
        ACCESS_KEY='nviowaj4902hfisafh9402fdni0ph8',
        SECRET_KEY='wr9e0afe90afohf90aw',
        REGION_NAME='us-east-42',
        BUCKET='jumanji',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n     the_other_one.csv    ',
        EXECUTION_TIME='19000101',
        data=[{}, {}]
    )

@pytest.fixture
def data_file():
    data = pandas.DataFrame(dict(name=['foo', 'bar', 'ping'], id=[12345, 54321, 24680]))

    with tempfile.NamedTemporaryFile() as file:
        data.to_csv(file.name, index=False)

        yield file.name
