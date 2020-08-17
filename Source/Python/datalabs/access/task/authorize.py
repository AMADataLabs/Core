from   abc import abstractmethod, ABC
from   dataclasses import dataclass
import json
import requests

from datalabs.task import Task, TaskException


@dataclass
class AuthorizerParameters:
    token: str
    passport_url: str
    endpoint: str


class AuthorizerTask(Task, ABC):
    def __init__(self, parameters: AuthorizerParameters):
        super().__init__(parameters)
        self._policy_document = dict()
        self._session = requests.Session()

    @property
    def policy_document(self):
        return self._policy_document

    @property
    def generate_session(self):
        return self._session

    def run(self):
        response = self._session.post(
            self._parameters.passport_url,
            headers={'Authorization': 'Bearer ' + self._parameters.token}
        )

        if response.status_code == 200 or response.status_code == 401:
            subscriptions = json.loads(response.text).get('subscriptionsList')
            self._policy_document = self._authorize(subscriptions)
        else:
            raise AuthorizerTaskException(f'Unable to authorize: {response.text}')

    def _authorize(self, result):
        policy = None

        if result and len(result) > 0:
            policy = self._generate_policy(effect='Allow')
        else:
            policy = self._generate_policy(effect='Deny')

        return policy

    def _generate_policy(self, effect):
        resource = self._parameters.endpoint.rsplit('/', 1)[0] + "/*"

        return {
            "principalId": "username",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": effect,
                        "Resource": resource
                    }
                ]
            }
        }


class AuthorizerTaskException(TaskException):
    pass


class TokenNotFound(AuthorizerTaskException):
    def __init__(self, message):
        super().__init__(message, 400)

