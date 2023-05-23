''' common test fixtures for datalabs.access.vericre.api modules '''
import pytest


@pytest.fixture
def profile_documents_event():
    return dict(
        path={},
        query={},
        authorization={},
        identity={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name=''
    )

@pytest.fixture
def ama_profile_pdf_event():
    return dict(
        path={},
        query={},
        authorization={},
        identity={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name='',
        client_id='',
        client_secret='',
        client_env=''
    )

@pytest.fixture
def caqh_profile_pdf_event():
    return dict(
        path={},
        query={},
        authorization={},
        identity={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name='',
        username='',
        password='',
        org_id='',
        application_type='',
        domain='',
        provider_api='',
        status_check_api=''
    )
