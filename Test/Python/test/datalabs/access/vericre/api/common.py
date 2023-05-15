''' common test fixtures for datalabs.access.vericre.api modules '''
import pytest


@pytest.fixture
def event():
    return dict(
        path={},
        query={},
        authorization={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name=''
    )
