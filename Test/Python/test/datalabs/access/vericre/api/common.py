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
        document_bucket=''
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
        document_bucket='',
        client_id='',
        client_secret='',
        token_url='',
        profile_url='',
        pdf_url=''
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
        document_bucket='',
        username='',
        password='',
        org_id='',
        application_type='',
        domain='',
        provider_api='',
        status_check_api=''
    )

@pytest.fixture
def physician_event():
    return dict(
        method='',
        path={},
        query={},
        authorization={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name='',
        physician_search_url='',
        sync_url='',
        payload={}
    )

@pytest.fixture
def multi_profile_lookup_event():
    return dict(
        method='',
        path={},
        query={},
        authorization={},
        database_host='',
        database_port='',
        database_backend='',
        database_name='',
        database_username='',
        database_password='',
        document_bucket_name='',
        payload={}
    )
