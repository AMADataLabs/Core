""" source: datalabs.etl.marketing.aggregate.transform """
import mock
import pytest

from   datalabs.access.atdata import AtData
from   datalabs.etl.marketing.aggregate.load import EmailValidationRequestLoaderTask
from   datalabs.etl.marketing.aggregate.transform import InputDataParser


# pylint: disable=redefined-outer-name
def test_email_validation_request_loader_read_data(data):
    assert len([InputDataParser.parse(x) for x in data]) == 2

    return  [InputDataParser.parse(x) for x in data]


# pylint: disable=protected-access, redefined-outer-name, line-too-long
def test_email_validation_request_loader_add_existing_validation_dates(transformer, data):
    dataset_with_emails, dataset_with_validation_dates = test_email_validation_request_loader_read_data(data)

    assert dataset_with_emails.shape[0] == 8
    assert dataset_with_emails.shape[1] == 3

    dated_dataset_with_emails = transformer._add_existing_validation_dates_to_emails(dataset_with_emails, dataset_with_validation_dates)

    assert dated_dataset_with_emails.shape[0] == 8
    assert dated_dataset_with_emails.shape[1] == 6
    assert 'id' in dated_dataset_with_emails.columns
    assert 'hs_contact_id' in dated_dataset_with_emails.columns
    assert 'email_last_validated' in dated_dataset_with_emails.columns
    assert not dated_dataset_with_emails['id'].isnull().any()
    assert not dated_dataset_with_emails['hs_contact_id'].isnull().any()
    assert not dated_dataset_with_emails['email_last_validated'].isnull().any()

    return dated_dataset_with_emails


# pylint: disable=protected-access, redefined-outer-name
def test_email_validation_request_loader_calculate_months_since_last_validated(transformer, data):
    dated_dataset_with_emails = test_email_validation_request_loader_add_existing_validation_dates(transformer, data)

    dated_dataset_with_emails = transformer._calculate_months_since_last_validated(dated_dataset_with_emails)

    assert not dated_dataset_with_emails['months_since_validated'].isnull().any()
    assert 'months_since_validated' in dated_dataset_with_emails.columns
    assert dated_dataset_with_emails.shape[1] == 7

    return dated_dataset_with_emails


# pylint: disable=protected-access, redefined-outer-name, line-too-long
def test_email_validation_request_loader_unset_update_flag_for_unexpired_emails(transformer, data):
    dated_dataset_with_emails = test_email_validation_request_loader_calculate_months_since_last_validated(transformer, data)

    dated_dataset_with_emails = transformer._unset_update_flag_for_unexpired_emails(dated_dataset_with_emails)

    assert dated_dataset_with_emails["months_since_validated"][0] == 9.0
    assert dated_dataset_with_emails["update"][0] is True

    assert dated_dataset_with_emails["months_since_validated"][1] == 5.0
    assert dated_dataset_with_emails["update"][1] is False

    return dated_dataset_with_emails


# pylint: disable=protected-access, redefined-outer-name, line-too-long
def test_email_validation_request_loader_get_expired_emails(transformer, data):
    dated_dataset_with_emails = test_email_validation_request_loader_unset_update_flag_for_unexpired_emails(transformer, data)
    email_data_list = transformer._get_expired_emails(dated_dataset_with_emails)

    assert len(email_data_list) == 3


# pylint: disable=protected-access, assignment-from-no-return, redefined-outer-name
def test_email_validation_request_loader(transformer, data, atdata_transformer, get_response):
    email_data_list = test_email_validation_request_loader_get_expired_emails(transformer, data)

    with mock.patch(
        "datalabs.access.atdata.AtData.request_email_validation",
        return_value=get_response
    ) as mock_json_load:

        mock_json_load.return_value=get_response.data
        request_parameters = atdata_transformer.request_email_validation(email_data_list)
        request_id, file = request_parameters[0], request_parameters[1]

    assert request_id == 'a318738'
    assert file is None

    return transformer._create_request_parameters_dict(request_parameters)


# pylint: disable=redefined-outer-name
@pytest.fixture
def data(dataset_with_emails_data, dataset_with_validation_dates_data):
    return [
        dataset_with_emails_data,
        dataset_with_validation_dates_data
    ]


# pylint: disable=redefined-outer-name
@pytest.fixture
def parameters(data):
    return dict(
        data=data,
        HOST='portal.freshaddress.com',
        ACCOUNT='AB254_16345',
        API_KEY='D02502F2-382A-4F8D-983E-3B3B82ABFD5B',
        MAX_MONTHS='6',
        EXECUTION_TIME='2023-10-17T00:00:00',
        LEFT_MERGE_KEY='EMPPID',
        RIGHT_MERGE_KEY='id'
    )


@pytest.fixture
def dataset_with_emails_data():
    return b"""EMPPID,LISTKEY,BEST_EMAIL
34797,X32#PBD#Z19#Z19#,psurati86@gmail.com
35627,X27#,ahnhs@korea.ac.kr
35824,PBD#WBR#X27#,jeremy@getpatch.com
34799,X32#,malloryj@northernmnnetwork.org
34796,SEL#,abby@primetimepartners.com
35829,X27#,jeremy@getpatch.com
35830,SEL#,dweepkumar@outlook.com
35831,PBD#,mt.michicainternational@gmail.com
"""


@pytest.fixture
def dataset_with_validation_dates_data():
    return b"""id,hs_contact_id,email_last_validated
34797,90ex1xXJjlAqyT6,1/1/2023
35627,4L1gUCqG6T2JTqb,5/1/2023
35824,1PE2wj4FrGXRQc6,5/13/2023
34799,uk6ogcgsH0Qjhrh,5/23/2023
34796,2STd4lNKbL9CzJk,8/23/2023
35829,1PE2wj4FrGXRQc6,6/13/2023
35830,qV4xRcwtZqMl62Z,1/1/2023
35831,JBB1mvrwX5nyGtP,10/1/2022
"""


# pylint: disable=redefined-outer-name
@pytest.fixture
def transformer(parameters):
    return EmailValidationRequestLoaderTask(parameters)


@pytest.fixture
def atdata_transformer():
    return AtData(host='portal.freshaddress.com',account='AB254_16345', api_key='D02502F2-382A-4F8D-983E-3B3B82ABFD5B')


@pytest.fixture
def get_response():
    mock_response = mock.Mock()
    mock_response.data = ['a318738', None]

    return mock_response
