import os

from datalabs.access.sftp import SFTP


import pytest


@pytest.mark.skip(reason="Example Usage")
def test_sftp_ls(sftp):
    info = sftp.ls('Data Analytics/Peter')

    assert len(info) > 0
    assert info[0].filename == 'foo'


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
