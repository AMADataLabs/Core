""" Pytest fixtures for test.datalabs.access """
import tempfile

import pytest


@pytest.fixture
def database_file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as file:
        yield file.name


# pylint: disable=redefined-outer-name
@pytest.fixture
def database_parameters(database_file):
    return dict(
        backend='sqlite',
        name=database_file,
        host='',
        port='',
        username='',
        password=''
    )
