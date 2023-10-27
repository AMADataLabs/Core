''' Performance profiling utilities. '''
import json
import urllib
from datetime import datetime
import logging

from datalabs.access.api.task import InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def run_time_logger(func):
    def wrapper(*args, **kwargs):
        start = datetime.now().isoformat()
        LOGGER.info("start: %s @%s", start, func.__name__)

        result = func(*args, **kwargs)

        end = datetime.now().isoformat()
        LOGGER.info("end: %s @%s", end, func.__name__)

        return result

    return wrapper


def get_ama_access_token(self, grant_type, client_id, client_secret):
    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_fields = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret
    }

    token_body = urllib.parse.urlencode(token_fields)
    token_response = request_ama_token(self, token_headers, token_body)

    if token_response.status != 200:
        raise InternalServerError(
            f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
        )

    return json.loads(token_response.data.decode("utf-8"))

# pylint: disable=protected-access
def request_ama_token(self, token_headers, token_body):
    return self.HTTP.request(
        'POST',
        self._parameters.token_url,
        headers=token_headers,
        body=token_body
    )
