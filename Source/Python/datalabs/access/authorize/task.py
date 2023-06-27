"""Authorize Task"""
from   dataclasses import dataclass
import logging
import json
import requests

from   datalabs.task import Task, TaskException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class AuthorizerParameters:
    token: str
    passport_url: str
    endpoint: str
    customer: str = None


class AuthorizerTask(Task):
    def __init__(self, parameters: AuthorizerParameters, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._authorization = {}
        self._session = requests.Session()

    @property
    def authorization(self):
        return self._authorization

    @property
    def generate_session(self):
        return self._session

    def run(self):
        headers = {
            'Authorization': 'Bearer ' + self._parameters.token,
        }

        if self._parameters.customer:
            headers["x-customer-nbr"] = self._parameters.customer

        response = self._session.post(
            self._parameters.passport_url,
            headers=headers
        )

        if response.status_code in (200, 401):
            entitlements = json.loads(response.text)
            LOGGER.info("Entitlements Response: %s", entitlements)

            self._authorization = self._authorize(entitlements)
        else:
            raise AuthorizerTaskException(f'Unable to authorize: {response.text}')

    def _authorize(self, entitlements):
        active_subscriptions = self._get_active_subscriptions(entitlements)
        customer_number = self._parameters.customer if self._parameters.customer else entitlements.get("customerNumber")
        policy = None
        context = dict(
            customerNumber=customer_number,
            customerName=entitlements.get("customerName")
        )

        if active_subscriptions is not None:
            policy = self._generate_policy(effect='Allow')
            context.update(self._generate_context_from_subscriptions(active_subscriptions))
        else:
            policy = self._generate_policy(effect='Deny')

        return {
            "principalId": "username",
            "context": context,
            "policyDocument": policy
        }

    @classmethod
    def _get_active_subscriptions(cls, entitlements):
        subscriptions = entitlements.get('subscriptionsList')
        active_subscriptions = None

        if subscriptions:
            active_subscriptions = [s for s in subscriptions if s.get("agreementStatus") == "A"]

        return active_subscriptions


    def _generate_policy(self, effect):
        base, stage, action, _ = self._parameters.endpoint.split('/', 3)
        resource = '/'.join((base, stage, action, '*'))

        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }

    @classmethod
    def _generate_context_from_subscriptions(cls, subscriptions):
        context = {}

        for subscription in subscriptions:
            context[subscription.get("productCode")] = subscription.get("accessEndDt")

        return context



class AuthorizerTaskException(TaskException):
    pass


class TokenNotFound(AuthorizerTaskException):
    def __init__(self, message):
        super().__init__(message, 400)
