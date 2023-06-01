import argparse
import base64
from   json.decoder import JSONDecodeError
import logging
import requests
import time

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PullRequestDecliner:
    def __init__(self, args):
        self._args = args
        self._verify_ssl = not args["no_verify_ssl"]

    def run(self):
        authorization_token = base64.b64encode(f'{self._args["user"]}:{self._args["password"]}'.encode()).decode()

        for id in self._pull_request_ids(authorization_token, self._args["title"]):
            LOGGER.info(f'Declining pull request {id}')
            response = self._decline_pull_request(authorization_token, id)
            time.sleep(1)

            LOGGER.info('Response to declining PR %s: %s', response.json()["id"], response.status_code)


    def _pull_request_ids(self, authorization_token, title):
        url = "https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/pullrequests"

        headers = {
           "Accept": "application/json",
           "Authorization": f"Basic {authorization_token}"
        }

        while url is not None:
            response = requests.request("GET", url, headers=headers, verify=self._verify_ssl)

            if response.status_code != 200:
                response.raise_for_status()

            pull_requests = self._get_pull_requests(response)

            for pull_request in pull_requests:
                if title == pull_request["title"]:
                    yield pull_request["id"]

            url = self._get_next_url(response)
            LOGGER.debug("Next URL: %s", url)


    def _decline_pull_request(self, authorization_token, id):
        url = f"https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/pullrequests/{id}/decline"
        response = None

        headers = {
           "Accept": "application/json",
           "Authorization": f"Basic {authorization_token}"
        }

        response = requests.request("POST", url, headers=headers, verify=self._verify_ssl)

        if response.status_code != 200:
            response.raise_for_status()

        return response


    @classmethod
    def _get_pull_requests(cls, response):
        pull_requests = []

        '''
        {
            'pagelen': 10,
            'size': 89,
            'values': [...],
            'page': 1,
            'next': 'https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/pullrequests?page=2'
        }
        '''

        if response.status_code == 200:
            pull_requests = response.json()["values"]

        return pull_requests


    @classmethod
    def _get_next_url(cls, response):
        url = None

        if response.status_code == 200:
            url = response.json().get("next")

        return url


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', required=True, help='Username')
    ap.add_argument('-p', '--password', required=True, help='Password')
    ap.add_argument('-t', '--title', required=True, help='Title')
    ap.add_argument('--no-verify-ssl', action="store_true", required=False, help='Disable SSL Verification')
    args = vars(ap.parse_args())

    PullRequestDecliner(args).run()
