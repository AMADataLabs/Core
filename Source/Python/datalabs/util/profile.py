''' Performance profiling utilities. '''
import json
import urllib
from datetime import datetime
import logging

import urllib3
import xmltodict

from datalabs.access.api.task import InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()

def run_time_logger(func):
    def wrapper(*args, **kwargs):
        start = datetime.now().isoformat()
        LOGGER.info("start: %s @%s", start, func.__name__)

        result = func(*args, **kwargs)

        end = datetime.now().isoformat()
        LOGGER.info("end: %s @%s", end, func.__name__)

        return result

    return wrapper

def get_ama_access_token(parameters):
    LOGGER.info("Getting AMA access token for client.")

    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_fields = {
        "grant_type": "client_credentials",
        "client_id": parameters.client_id,
        "client_secret": parameters.client_secret
    }
    token_body = urllib.parse.urlencode(token_fields)

    token_response = _request_ama_token(token_headers, token_body, parameters.token_url)

    if token_response.status != 200:
        raise InternalServerError(
            f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
        )

    token_json = json.loads(token_response.data)
    
    return token_json['access_token']

def _request_ama_token(token_headers, token_body, token_url):
    return HTTP.request(
        'POST',
        token_url,
        headers=token_headers,
        body=token_body
    )

def parse_xml_to_dict(xml):
    return xmltodict.parse(
        xml.decode("utf-8"), 
        xml_attribs=False, 
        postprocessor=_xml_format_converter
    )

# pylint: disable=unused-argument
def _xml_format_converter(path, key, value):
    if value is not None and type(value) is str:
        try:
            return key, int(value)
        except ValueError:
            if value.lower() == 'true':
                return key, True
            elif value.lower() == 'false':
                return key, False
            else:
                return key, value
    else:
        return key, value
