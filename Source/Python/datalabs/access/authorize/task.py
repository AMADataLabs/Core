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
        response = self._session.post(
            self._parameters.passport_url,
            headers={'Authorization': 'Bearer ' + self._parameters.token}
        )

        if response.status_code in (200, 401):
            entitlements = json.loads(response.text)
            LOGGER.info("Entitlements Response: %s", entitlements)

            self._authorization = self._authorize(entitlements)
        else:
            raise AuthorizerTaskException(f'Unable to authorize: {response.text}')

    def _authorize(self, entitlements):
        policy = None
        context = dict(
            customerNumber=entitlements.get("customerNumber"),
            customerName=entitlements.get("customerName")
        )
        active_subscriptions = self._get_active_subscriptions(entitlements)

        if active_subscriptions and len(active_subscriptions) > 0:
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
        return [s for s in entitlements.get('subscriptionsList') if s.get("agreementStatus") == "A"]


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
