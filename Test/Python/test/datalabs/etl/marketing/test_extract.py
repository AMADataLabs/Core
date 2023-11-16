""" source: datalabs.etl.marketing.aggregate.transform """
import mock
import pytest

from   datalabs.access.atdata import AtData
from   datalabs.etl.marketing.aggregate.extract import EmailValidationExtractorTask
from   datalabs.etl.marketing.aggregate.transform import InputDataParser


# pylint: disable=redefined-outer-name
def read_dated_dataset_with_emails_data(data):
    return  [InputDataParser.parse(x) for x in data]


# pylint: disable=redefined-outer-name
def test_email_validation_extractor_validate_emails(atdata_transformer, request_parameters_data, get_response):
    with mock.patch(
        "datalabs.access.atdata.AtData.get_validation_results",
        return_value=get_response
    ) as mock_json_load:
        mock_json_load.return_value=get_response.data
        validated_emails = atdata_transformer.get_validation_results(
            request_parameters_data["request_id"],
            request_parameters_data["results_filename"]
        )

    assert validated_emails ==  ['dweepkumar@outlook.com', 'psurati86@gmail.com']

    return validated_emails


# pylint: disable=redefined-outer-name, line-too-long, protected-access
def test_email_validation_extractor_set_update_flag_for_valid_emails(transformer, atdata_transformer, request_parameters_data, get_response, data):
    dated_dataset_with_emails = read_dated_dataset_with_emails_data(data)[0]

    validated_emails = test_email_validation_extractor_validate_emails(
        atdata_transformer,
        request_parameters_data,
        get_response
    )
    dated_dataset_with_emails = transformer._set_update_flag_for_valid_emails(
        dated_dataset_with_emails,
        validated_emails
    )

    assert dated_dataset_with_emails["update"].tolist() == [True, False, False, False, False, False, True, False]

    return dated_dataset_with_emails


# pylint: disable=redefined-outer-name, line-too-long, protected-access
def test_email_validation_extractor_remove_invalid_records(transformer, atdata_transformer, request_parameters_data, get_response, data):
    dated_dataset_with_emails = test_email_validation_extractor_set_update_flag_for_valid_emails(transformer, atdata_transformer, request_parameters_data, get_response, data)

    dated_dataset_with_emails = transformer._remove_invalid_records(dated_dataset_with_emails)

    assert dated_dataset_with_emails.shape[0] == 8
    assert dated_dataset_with_emails.shape[1] == 8

    return dated_dataset_with_emails


# pylint: disable=protected-access, line-too-long
def test_email_validation_extractor_update_email_last_validated(transformer, atdata_transformer, request_parameters_data, get_response, data):
    dated_dataset_with_emails = test_email_validation_extractor_remove_invalid_records(
        transformer,
        atdata_transformer,
        request_parameters_data,
        get_response,
        data
    )

    assert dated_dataset_with_emails.email_last_validated[0] == '1/16/2023'
    assert dated_dataset_with_emails.email_last_validated[1] == '5/1/2023'
    assert dated_dataset_with_emails.email_last_validated[6] == '1/1/2023'

    dated_dataset_with_emails = transformer._update_email_last_validated(dated_dataset_with_emails)

    assert dated_dataset_with_emails.email_last_validated[0] == '10/17/2023'
    assert dated_dataset_with_emails.email_last_validated[1] == '5/1/2023'
    assert dated_dataset_with_emails.email_last_validated[6] == '10/17/2023'


@pytest.fixture
def atdata_parameters():
    return dict(
        host='portal.freshaddress.com',
        account='AB254_16345',
        api_key='D02502F2-382A-4F8D-983E-3B3B82ABFD5B'
    )


# pylint: disable=redefined-outer-name
@pytest.fixture
def parameters(data):
    return dict(
        data=data,
        HOST='portal.freshaddress.com',
        ACCOUNT='AB254_16345',
        API_KEY='D02502F2-382A-4F8D-983E-3B3B82ABFD5B',
        MAX_MONTHS='6',
        EXECUTION_TIME='2023-10-17T00:00:00'
    )


@pytest.fixture
def atdata_transformer():
    return AtData(
        host='portal.freshaddress.com',
        account='AB254_16345',
        api_key='D02502F2-382A-4F8D-983E-3B3B82ABFD5B'
    )


# pylint: disable=redefined-outer-name
@pytest.fixture
def transformer(parameters):
    return EmailValidationExtractorTask(parameters)


@pytest.fixture
def get_response():
    mock_response = mock.Mock()
    mock_response.data = ['dweepkumar@outlook.com', 'psurati86@gmail.com']

    return mock_response


@pytest.fixture
def request_parameters_data():
    return dict(
        request_id="a319725",
        results_filename="emails_20231102-152626_Results_12.txt"
    )


# pylint: disable=redefined-outer-name
@pytest.fixture
def data(dated_dataset_with_emails):
    return [dated_dataset_with_emails]


@pytest.fixture
def dated_dataset_with_emails():
    return b"""EMPPID,LISTKEY,BEST_EMAIL,id,hs_contact_id,email_last_validated,months_since_validated,update
34797,X32#PBD#Z19#Z19#,psurati86@gmail.com,34797,90ex1xXJjlAqyT6,1/16/2023,9.0,True
35627,X27#,ahnhs@korea.ac.kr,35627,4L1gUCqG6T2JTqb,5/1/2023,5.0,False
35824,PBD#WBR#X27#,jeremy@getpatch.com,35824,1PE2wj4FrGXRQc6,5/13/2023,5.0,False
34799,X32#,malloryj@northernmnnetwork.org,34799,uk6ogcgsH0Qjhrh,5/23/2023,4.0,False
34796,SEL#,abby@primetimepartners.com,34796,2STd4lNKbL9CzJk,8/23/2023,1.0,False
35829,X27#,jeremy@getpatch.com,35829,1PE2wj4FrGXRQc6,6/13/2023,4.0,False
35830,SEL#,dweepkumar@outlook.com,35830,qV4xRcwtZqMl62Z,1/1/2023,9.0,True
35831,PBD#,mt.michicainternational@gmail.com,35831,JBB1mvrwX5nyGtP,10/1/2022,12.0,True
"""
