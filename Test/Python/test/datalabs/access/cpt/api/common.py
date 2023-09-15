''' common test fixtures for datalabs.access.cpt.api modules '''
import pytest


@pytest.fixture
def event():
    return dict(
        method="GET",
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


@pytest.fixture
def search_parameters():
    return dict(
        results=None,
        index='SampleIndexName',
        keywords='test|these|keywords',
        sections='test|sections',
        subsections='test|subsections',
        updated_date_from='2022-01-01',
        updated_date_to='2023-09-10'
    )
