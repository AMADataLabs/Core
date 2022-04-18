""" source: datalabs.etl.sftp.extract """
import mock
import pytest

import datalabs.etl.sftp.extract as sftp


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_are_deserialized(parameters):

    with mock.patch('datalabs.access.sftp.SFTP'):
        task = sftp.SFTPFileExtractorTask(parameters)

        assert isinstance(task._parameters, sftp.SFTPFileExtractorParameters)


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('datalabs.access.sftp'):
        task = sftp.SFTPFileExtractorTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_base_path_works(parameters):
    with mock.patch('datalabs.access.sftp'):
        parameters['BASE_PATH'] = 'dir1/%Y%m%d/dir2/dir3'
        task = sftp.SFTPFileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/19000101/dir2/dir3/the_other_one.csv'


# pylint: disable=redefined-outer-name, protected-access
def test_datetime_formatting_in_file_works(parameters):
    with mock.patch('datalabs.access.sftp'):
        parameters['FILES'] = 'this_one.csv,that_one.csv,\n       the_other_%Y%m%d_one.csv     '
        task = sftp.SFTPFileExtractorTask(parameters)

        files = task._get_files()
        resolved_files = task._resolve_files(files)

        assert len(resolved_files) == 3
        assert resolved_files[2] == 'dir1/dir2/dir3/the_other_19000101_one.csv'


def test_ibm437_decoding(parameters):
    task = sftp.SFTPIBM437TextFileExtractorTask(parameters)
    ibm437_encoded_text = '▒'.encode('ibm437')
    unicode_encoded_text = task._decode_data(ibm437_encoded_text)

    assert unicode_encoded_text == '▒'.encode("utf-8")

def test_cp1252_decoding(parameters):
    task = sftp.SFTPWindowsTextFileExtractorTask(parameters)
    cp1252_encoded_text = '¥'.encode('cp1252')
    unicode_encoded_text = task._decode_data(cp1252_encoded_text)

    assert unicode_encoded_text == '¥'.encode("utf-8")

@pytest.fixture
def parameters():
    return dict(
        HOST='bogus.host.fqdn',
        USERNAME='fsoaf90w',
        PASSWORD='dfihas80',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )
