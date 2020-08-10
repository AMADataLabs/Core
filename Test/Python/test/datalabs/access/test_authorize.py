import pytest
import mock
import datalabs.access.authorize as authorizer


def test_authorized(authorized_passport_response):
    with mock.patch('datalabs.access.authorize.AuthorizerTask.run') as post:
        # assert post.call_count == 1
        post.return_value = authorized_passport_response
        policy_document = authorizer.AuthorizerTask._check_response(authorized_passport_response.get('subscriptionsList'))
        assert policy_document.get('policyDocument').get('Statement')[0].get('Effect') == 'Allow'


def test_not_authorized(unauthorized_passport_response):
    with mock.patch('datalabs.access.authorize.AuthorizerTask.run') as post:
        # assert post.call_count == 1
        post.return_value = unauthorized_passport_response
        policy_document = authorizer.AuthorizerTask._check_response(unauthorized_passport_response.get('subscriptionsList'))
        assert policy_document.get('policyDocument').get('Statement')[0].get('Effect') == 'Deny'


@pytest.fixture
def unauthorized_passport_response():
    return {
        "returnCode": 0,
        "returnMessage": "SUCCESS",
        "customerNumber": "000003570999",
        "customerName": "Cahaba Medical Center - Maplesville",
        "responseId": "7d7e2836-1c2d-4a13-a0fe-8bd58c92d7c5",
        "subscriptionsList": []
    }


@pytest.fixture
def authorized_passport_response():
    return {
        "returnCode": 0,
        "returnMessage": "SUCCESS",
        "customerNumber": "000003570997",
        "customerName": "Chelsea Village Medical Office",
        "responseId": "421c3e7e-843c-4846-8b4b-a0093b1762f7",
        "subscriptionsList": [
            {
                "accessEndDt": "2021-06-19-05:00",
                "expirationDt": "2021-06-19-05:00",
                "productCode": "CPTAPI",
                "agreementStatus": "A",
                "subscriptionId": 6613481,
                "asOfDate": "2020-08-06-08:39",
                "startDate": "2020-06-20-05:00"
            }
        ]
    }
