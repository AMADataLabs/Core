''' common test fixtures for datalabs.access.cpt.api modules '''
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
        bucket='',
        base_path='',
        url_duration=''
    )
