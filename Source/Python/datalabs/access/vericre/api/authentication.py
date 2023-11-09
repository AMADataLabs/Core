""" API endpoint task classes. """
import logging
import json
import urllib

import urllib3

from datalabs.access.api.task import InternalServerError

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()


class EProfilesAuthenticatingEndpointMixin:
    @classmethod
    def _authenticate_to_eprofiles(cls, parameters, headers):
        access_token = cls._get_passport_access_token(parameters)

        headers["Authorization"] = f"Bearer {access_token}"

    @classmethod
    def _get_eprofiles_access_token(cls, parameters):
        LOGGER.info("Getting AMA access token for client.")

        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_fields = {
            "grant_type": "client_credentials",
            "client_id": parameters.client_id,
            "client_secret": parameters.client_secret,
        }
        token_body = urllib.parse.urlencode(token_fields)

        token_response = cls._request_eprofiles_access_token(token_headers, token_body, parameters.token_url)

        if token_response.status != 200:
            raise InternalServerError(
                f"Internal Server error caused by: {token_response.data}, status: {token_response.status}"
            )

        token_json = json.loads(token_response.data)

        return token_json["access_token"]

    @classmethod
    def _request_eprofiles_access_token(cls, token_headers, token_body, token_url):
        return HTTP.request("POST", token_url, headers=token_headers, body=token_body)
