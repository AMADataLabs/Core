import argparse
import base64
from   json.decoder import JSONDecodeError
import logging
import requests
import time

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(args):
    authorization_token = base64.b64encode(f'{args["user"]}:{args["password"]}'.encode()).decode()

    for id in _pull_request_ids(authorization_token, args["title"]):
        LOGGER.info(f'Declining pull request {id}')
        response = _decline_pull_request(authorization_token, id)
        time.sleep(1)

        LOGGER.info('Response to declining PR %s: %s', response.json()["id"], response.status_code)

def _pull_request_ids(authorization_token, title):
    url = "https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/pullrequests"

    headers = {
       "Accept": "application/json",
       "Authorization": f"Basic {authorization_token}"
    }

    while url is not None:
        response = requests.request("GET", url, headers=headers)

        pull_requests = _get_pull_requests(response)

        for pull_request in pull_requests:
            if title == pull_request["title"]:
                yield pull_request["id"]

        url = _get_next_url(response)
        LOGGER.debug("Next URL: %s", url)


def _decline_pull_request(authorization_token, id):
    url = f"https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/pullrequests/{id}/decline"

    headers = {
       "Accept": "application/json",
       "Authorization": f"Basic {authorization_token}"
    }

    return requests.request("POST", url, headers=headers)


def _get_pull_requests(response):
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


def _get_next_url(response):
    url = None

    if response.status_code == 200:
        url = response.json().get("next")

    return url


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', required=True, help='Username')
    ap.add_argument('-p', '--password', required=True, help='Password')
    ap.add_argument('-t', '--title', required=True, help='Title')
    args = vars(ap.parse_args())

    main(args)
