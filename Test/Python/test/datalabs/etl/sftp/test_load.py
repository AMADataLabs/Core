""" source: datalabs.etl.sftp.load """
import mock
import pytest

import datalabs.etl.sftp.load as sftp


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):

    with mock.patch('datalabs.access.sftp.SFTP'):
        task = sftp.SFTPFileLoaderTask(parameters)

        assert isinstance(task._parameters, sftp.SFTPFileLoaderParameters)


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('datalabs.access.sftp'):
        task = sftp.SFTPFileLoaderTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_base_path_works(parameters):
    with mock.patch('datalabs.access.sftp'):
        parameters['BASE_PATH'] = 'dir1/%Y%m%d/dir2/dir3'
        task = sftp.SFTPFileLoaderTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/19000101/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_file_works(parameters):
    with mock.patch('datalabs.access.sftp'):
        parameters['FILES'] = 'this_one.csv,that_one.csv,\n       the_other_%Y%m%d_one.csv     '
        task = sftp.SFTPFileLoaderTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/dir2/dir3/the_other_19000101_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_UTF8_encoding(parameters):
    task = sftp.SFTPWindowsTextFileLoaderTask(parameters)
    encoded = 'a1b2c3d4e5'.encode('utf-8')
    resolved_files = task._encode_data(encoded)

    assert resolved_files == 'a1b2c3d4e5'.encode('cp1252')

@pytest.fixture
def parameters():
    return dict(
        HOST='bogus.host.fqdn',
        USERNAME='fsoaf90w',
        PASSWORD='dfihas80',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101',
        data=[{}, {}]
    )


