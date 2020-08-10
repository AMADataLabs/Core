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
        self._status_code = 200
        self._response_body = dict()
        self._headers = dict()
        self._session = requests.Session()

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    @property
    def generate_session(self):
        return self._session

    @property
    def headers(self):
        return self._headers

    def run(self):
        response = self._session.post(
            self._parameters.passport_url,
            headers={'Authorization': 'Bearer ' + self._parameters.token}
        )

        if response.status_code == 200:
            subscriptions = json.loads(response.text).get('subscriptionsList')
            self._response_body = self._authorize(subscriptions)
        else:
            raise AuthorizerTaskException(f'Unable to authorize: {response.text}', status_code=response.status_code)

    def _authorize(self, result):
        policy = None

        if len(result) > 0:
            policy = self._generate_policy(effect='Allow')
        else:
            policy = self._generate_policy(effect='Deny')

        return policy

    def _generate_policy(self, effect):
        return {
            "principalId": "username",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": effect,
                        "Resource": self._parameters.endpoint
                    }
                ]
            }
        }


class AuthorizerTaskException(TaskException):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request

    @property
    def status_code(self):
        return self._status_code


class TokenNotFound(AuthorizerTaskException):
    def __init__(self, message):
        super().__init__(message, 400)
