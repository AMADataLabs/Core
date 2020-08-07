import json
import requests
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datalabs.task import Task, TaskException

from datalabs.access.orm import DatabaseTaskMixin


@dataclass
class AuthorizerParameters:
    token: str
    passport_url: str


class AuthorizerTask(Task, DatabaseTaskMixin, ABC):
    def __init__(self, parameters: AuthorizerParameters):
        super().__init__(parameters)
        self._status_code = 200
        self._response_body = dict()
        self._headers = dict()
        self.session = requests.Session()

    @property
    def status_code(self):
        return self._status_code

    @property
    def response_body(self):
        return self._response_body

    @property
    def generate_session(self):
        return self.session

    @property
    def headers(self):
        with self._parameters.token as token:
            self._headers = {'Authorization': 'Bearer ' + token}
        return self._headers

    def run(self):
        with self._parameters.passport_url as url:
            result = self.session.post(url, headers=self.headers)

        if result.status_code == 200 and len(json.loads(result.text).get('subscriptionsList')) > 0:
            return self.generate_policy(effect='Allow')
        else:
            return self.generate_policy(effect='Deny')

    def generate_policy(self, effect):
        self._response_body = {"principalId": "my-username",
                               "policyDocument": {
                                   "Version": "2012-10-17",
                                   "Statement": [
                                       {
                                           "Action": "execute-api:Invoke",
                                           "Effect": effect,
                                           "Resource": "arn:aws:lambda:us-east-1:644454719059:function:CPTDefault"
                                       }]
                               }
                               }
        return self._response_body

    @abstractmethod
    def _run(self, session):
        pass


class AuthorizerTaskException(TaskException):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request

    @property
    def status_code(self):
        return self._status_code


class InvalidRequest(AuthorizerTaskException):
    pass


class ResourceNotFound(AuthorizerTaskException):
    def __init__(self, message):
        super().__init__(message, 404)


class InternalServerError(AuthorizerTaskException):
    def __init__(self, message):
        super().__init__(message, 500)
