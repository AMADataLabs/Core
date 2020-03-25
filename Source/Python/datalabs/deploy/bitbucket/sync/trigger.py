import base64
import logging
import os
import flask
import hashlib
import hmac

import settings
import werkzeug.exceptions as exceptions

import datalabs.deploy.bitbucket.sync.sync as sync

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

routes = flask.Blueprint('trigger', __name__)


@routes.route('/', methods=['POST'])
def sync_bitbucket():
    _verify_secret_key(flask.request.data, flask.request.headers.get('X-Hub-Signature'))

    response = _sync_on_prem_with_cloud_bitbucket(flask.request.json)

    return flask.jsonify(response)


def _verify_secret_key(request_data, request_signature):
    secret_key = os.environ.get('SECRET_KEY')

    calculated_signature = _sign_request_data(request_data, secret_key)
    LOGGER.debug('Request signature: %s', request_signature)
    LOGGER.debug('Calculated signature: %s', calculated_signature)

    if request_signature != calculated_signature:
        raise exceptions.BadRequest('The request data signature is invalid.')


def _sync_on_prem_with_cloud_bitbucket(request_data)
    config = _generate_sync_configuration()
    synchronizer = sync.BitBucketSynchronizer(config)

    LOGGER.debug('Trigger Request: %s', request_data)
    return synchronizer.sync(request_data)


def _sign_request_data(request_data, secret_key):
    message = bytes(request_data, 'utf-8')
    secret = bytes(secret_key, 'utf-8')

    return base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())

def _generate_sync_configuration():
    return sync.Configuration(
        url_on_prem=os.environ.get('URL_ON_PREMISES'),
        url_cloud=os.environ.get('URL_CLOUD'),
    )
