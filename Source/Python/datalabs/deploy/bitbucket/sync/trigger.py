""" BitBucket sync trigger route. """

import logging
import os
import hashlib
import hmac

import flask
from   werkzeug import exceptions

from   datalabs.deploy.bitbucket.sync import sync

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

ROUTES = flask.Blueprint('trigger', __name__)


@ROUTES.route('/', methods=['POST'])
def sync_bitbucket():
    request_signature = flask.request.headers.get('X-Hub-Signature')

    try:
        _verify_secret_key(flask.request.data, request_signature)

        response = _sync_on_prem_with_cloud_bitbucket(flask.request.json)
    except exceptions.BadRequest as exception:
        if _is_test_data(flask.request.json):
            response = {'alive': True}
        else:
            raise exception

    return flask.jsonify(response)


def _verify_secret_key(request_data, request_signature):
    LOGGER.debug('Request Data: %s', request_data)
    LOGGER.debug('Request Signature: %s', request_signature)
    secret_key = os.environ.get('SECRET_KEY')

    calculated_signature = _sign_request_data(request_data, secret_key)
    LOGGER.debug('Calculated signature: %s', calculated_signature)

    if request_signature != calculated_signature:
        raise exceptions.BadRequest('The request data signature is invalid.')


def _sync_on_prem_with_cloud_bitbucket(request_data):
    config = _generate_sync_configuration()
    synchronizer = sync.BitBucketSynchronizer(config)

    LOGGER.debug('Trigger Request: %s', request_data)
    return synchronizer.sync(request_data)

def _is_test_data(request_data):
    return request_data.get('test')


def _sign_request_data(request_data, secret_key):
    message = request_data
    secret = bytes(secret_key, 'utf-8')

    return 'sha256=' + hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()

def _generate_sync_configuration():
    return sync.Configuration(
        url_on_prem=os.environ.get('URL_ON_PREMISES'),
        url_cloud=os.environ.get('URL_CLOUD'),
    )
