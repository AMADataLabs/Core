import logging
import os
import flask

import settings

import datalabs.deploy.bitbucket.sync.sync as sync

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

routes = flask.Blueprint('trigger', __name__)


@routes.route('/', methods=['POST'])
def sync_bitbucket():
    data = flask.request.json
    config = _generate_sync_configuration()
    synchronizer = sync.BitBucketSynchronizer(config)

    LOGGER.debug('Trigger Request: %s', data)
    response = synchronizer.sync(data)

    return flask.jsonify(response)


def _generate_sync_configuration():
    return sync.Configuration(
        url_on_prem=os.environ.get('URL_ON_PREMISES'),
        url_cloud=os.environ.get('URL_CLOUD'),
        user_on_prem=os.environ.get('USER_ON_PREMISES'),
    )
