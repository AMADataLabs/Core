""" source: datalabs.access.environment """
import pytest
from   datalabs.access.sftp import SFTP


# pylint: disable=redefined-outer-name
@pytest.mark.skip(reason="Example Usage")
def test_sftp_ls(sftp):
    files = sftp.ls('Data Analytics/Baseline/data', filter='PhysicianProfessionalDataFile_*')

    assert len(files) > 0

    for file in files:
        assert file.startswith('PhysicianProfessionalDataFile_')


@pytest.fixture
def sftp():
    """ Connect to SFTP using CREDENTIALS_SFTP_USERNAME and CREDENTIALS_SFTP_PASSWORD """
    # pylint: disable=redefined-outer-name
    with SFTP() as sftp:
        yield sftp
