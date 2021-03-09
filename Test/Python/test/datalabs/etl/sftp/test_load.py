""" source: datalabs.etl.sftp.load """
import mock
import pytest

import datalabs.etl.sftp.load as sftp


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    with mock.patch('datalabs.access.sftp'):
        task = sftp.SFTPFileLoaderTask(parameters)

        files = task._get_files()

        assert len(files) == 3
        assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


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
