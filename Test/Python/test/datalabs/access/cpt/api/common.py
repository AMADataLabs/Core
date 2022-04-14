''' common test fixtures for datalabs.access.cpt.api modules '''
import pytest


@pytest.fixture
def event():
    return dict(
        path=dict(),
        query=dict(),
        authorization={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        bucket_name='',
        bucket_base_path='',
        bucket_url_duration=''
    )
