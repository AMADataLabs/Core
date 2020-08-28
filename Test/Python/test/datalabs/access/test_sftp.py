import os

from datalabs.access.sftp import SFTP


import pytest


@pytest.mark.skip(reason="Example Usage")
def test_sftp_ls(sftp):
    files = sftp.ls('Data Analytics/Baseline/data', filter='PhysicianProfessionalDataFile_*')

    assert len(files) > 0

    for file in files:
        assert file.startswith('PhysicianProfessionalDataFile_')


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['CREDENTIALS_DEFAULT_USERNAME'] = '{{ username }}'
    os.environ['CREDENTIALS_DEFAULT_PASSWORD'] = '{{ password }}'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


@pytest.fixture
def sftp(environment):
    with SFTP() as sftp:
        yield sftp
