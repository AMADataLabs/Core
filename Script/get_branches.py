import argparse
import base64
from   json.decoder import JSONDecodeError
import logging
import requests

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def main(args):
    authorization_token = base64.b64encode(f'{args["user"]}:{args["password"]}'.encode()).decode()

    for branch_name in _branch_names(authorization_token, args["prefix"]):
        print(branch_name)

def _branch_names(authorization_token, prefix):
    url = "https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/refs/branches"


    headers = {
       "Accept": "application/json",
       "Authorization": f"Basic {authorization_token}"
    }

    while url is not None:
        response = requests.request("GET", url, headers=headers)

        branches = _get_branches(response)

        for branch in branches:
            if prefix is None or (prefix is not None and branch["name"].startswith(prefix)):
                yield branch["name"]

        url = _get_next_url(response)
        LOGGER.debug("Next URL: %s", url)


def _get_branches(response):
    pull_requests = []

    '''
    {
        'pagelen': 10,
        'size': 89,
        'values': [...],
        'page': 1,
        'next': 'https://api.bitbucket.org/2.0/repositories/amaappdev/hs-datalabs/refs/branches?page=2'
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
    ap.add_argument('-x', '--prefix', required=False, help='Branch name prefix')
    args = vars(ap.parse_args())

    main(args)
