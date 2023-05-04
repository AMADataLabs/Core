''' common test fixtures for datalabs.access.vericre.api modules '''
import pytest


@pytest.fixture
def profile_documents_event():
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

@pytest.fixture
def ama_profile_pdf_event():
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
        client_id='428b5f8e-c591-4630-a565-de2b407a5db8',
        client_secret='287e077a-a447-49b1-9c15-d49c9bb92f61',
        client_env='wsextstage'
    )

@pytest.fixture
def caqh_profile_pdf_event():
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
        username='',
        password='',
        org_id='',
        application_type='',
        domain='',
        provider_api='',
        status_check_api=''
    )