""" source: datalabs.access.authorize.awslambda """
from collections import namedtuple
import mock

import pytest

from datalabs.access.authorize.task import AuthorizerTask


# pylint: disable=redefined-outer-name
def test_authorized_with_active_subscriptions(active_subscriptions_passport_response, parameters):
    authorizer = AuthorizerTask(parameters)

    with mock.patch("requests.Session.post") as post:
        post.return_value = active_subscriptions_passport_response
        authorizer.run()

        assert authorizer.authorization.get("policyDocument").get("Statement")[0].get("Effect") == "Allow"


# pylint: disable=redefined-outer-name
def test_authorized_with_no_subscriptions(no_subscriptions_passport_response, parameters):
    authorizer = AuthorizerTask(parameters)

    with mock.patch("requests.Session.post") as post:
        post.return_value = no_subscriptions_passport_response
        authorizer.run()

        assert authorizer.authorization.get("policyDocument").get("Statement")[0].get("Effect") == "Allow"


# pylint: disable=redefined-outer-name
def test_not_authorized(unauthorized_passport_response, parameters):
    parameters["customer"] = "000003570999"
    authorizer = AuthorizerTask(parameters)

    with mock.patch("requests.Session.post") as post:
        post.return_value = unauthorized_passport_response
        authorizer.run()

        assert authorizer.authorization.get("policyDocument").get("Statement")[0].get("Effect") == "Deny"

        context = authorizer.authorization.get("context")
        assert len(context) == 2
        assert context.get("customerName") is None
        assert context.get("customerNumber") == "000003570999"


# pylint: disable=redefined-outer-name
def test_authorization_contains_subscriptions(active_subscriptions_passport_response, parameters):
    parameters["customer"] = "000003570997"
    authorizer = AuthorizerTask(parameters)

    with mock.patch("requests.Session.post") as post:
        post.return_value = active_subscriptions_passport_response
        authorizer.run()

        context = authorizer.authorization.get("context")
        assert len(context) == 3
        assert context.get("customerNumber") == "000003570997"
        assert context.get("customerName") == "Chelsea Village Medical Office"
        assert context.get("CPTAPI") == '{"start": "2020-06-20-05:00", "end": "2021-06-19-05:00"}'


# pylint: disable=redefined-outer-name
def test_invalid_user_authorization_returns_no_subscriptions(bad_user_passport_response, parameters):
    authorizer = AuthorizerTask(parameters)

    with mock.patch("requests.Session.post") as post:
        post.return_value = bad_user_passport_response
        authorizer.run()

        context = authorizer.authorization.get("context")
        assert len(context) == 2
        assert context.get("customerNumber") is None
        assert context.get("customerName") is None


@pytest.fixture
def parameters():
    return dict(
        token="fj9d0ayf40y04tyq0yfdaso",
        passport_url="https://passport-foo.ama-assn.org",
        endpoint="arn:aws:execute-api:us-east-1:123456789012:abcdef1234/ESTestInvoke-stage/GET/Function",
    )


PassportResponse = namedtuple("PassportResponse", "status_code, text")


@pytest.fixture
def unauthorized_passport_response():
    return PassportResponse(
        status_code=401,
        text="""
            {
                "returnCode": null,
                "returnMessage": null,
                "customerNumber": null,
                "customerName": null,
                "responseId": null,
                "subscriptionsList": null
            }
        """,
    )


@pytest.fixture
def active_subscriptions_passport_response():
    return PassportResponse(
        status_code=200,
        text="""
            {
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
                    },
                    {
                        "accessEndDt": "2021-06-19-05:00",
                        "expirationDt": "2021-06-19-05:00",
                        "productCode": "STUFF",
                        "agreementStatus": "I",
                        "subscriptionId": 6613481,
                        "asOfDate": "2020-08-06-08:39",
                        "startDate": "2020-06-20-05:00"
                    }
                ]
            }
        """,
    )


@pytest.fixture
def no_subscriptions_passport_response():
    return PassportResponse(
        status_code=200,
        text="""
            {
                "returnCode": 0,
                "returnMessage": "SUCCESS",
                "customerNumber": "000003570997",
                "customerName": "Chelsea Village Medical Office",
                "responseId": "421c3e7e-843c-4846-8b4b-a0093b1762f7",
                "subscriptionsList": []
            }
        """,
    )


@pytest.fixture
def bad_user_passport_response():
    return PassportResponse(
        status_code=200,
        text="""
            {
                "returnCode": null,
                "returnMessage": null,
                "customerNumber": null,
                "customerName": null,
                "responseId": null,
                "subscriptionsList": null
            }
        """,
    )
