import json
import requests
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datalabs.task import Task, TaskException


@dataclass
class AuthorizerParameters:
    token: str
    passport_url: str


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
        result = self._session.post(
            self._parameters.passport_url,
            headers={'Authorization': 'Bearer ' + self._parameters.token}
        )

        if result.status_code == 200:
            subscriptions = json.loads(result.text).get('subscriptionsList')
            policy = self._authorize(subscriptions)
        else:
            raise TokenNotFound('Invalid authorization token')

    @classmethod
    def _authorize(cls, result):
        policy = None

        if len(result) > 0:
            policy = cls._generate_policy(effect='Allow')
        else:
            policy = cls._generate_policy(effect='Deny')

        return policy

    @classmethod
    def _generate_policy(cls, effect):
        return {
            "principalId": "my-username",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": effect,
                        # TODO: this needs to be the dynamically-created ARN of the endpoint we're authorizing
                        "Resource": "arn:aws:lambda:us-east-1:644454719059:function:CPTDefault"
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
