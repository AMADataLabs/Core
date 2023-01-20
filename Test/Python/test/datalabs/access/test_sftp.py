""" source: datalabs.access.environment """
import os

import pytest
from   datalabs.access.sftp import SFTP


# pylint: disable=redefined-outer-name
@pytest.mark.skip(reason="Example Usage")
def test_sftp_ls(parameters):
    with SFTP(parameters) as sftp:
        files = sftp.list('Data Analytics/Baseline/data', filter='PhysicianProfessionalDataFile_*')

    assert len(files) > 0

    for file in files:
        assert file.startswith('PhysicianProfessionalDataFile_')


@pytest.fixture
def parameters():
    return dict(
        username=os.environ["SFTP_USERNAME"],
        password=os.environ["SFTP_PASSWORD"]
    )
