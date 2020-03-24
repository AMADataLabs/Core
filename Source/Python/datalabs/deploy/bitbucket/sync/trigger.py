import flask

import settings

import datalabs.deploy.bitbucket.sync.sync as sync

routes = flask.Blueprint('trigger', __name__)


@routes.route('/', methods=['POST'])
def sync_bitbucket():
    data = flask.request.get_json()
    config = _generate_sync_configuration()
    synchronizer = sync.BitBucketSynchronizer(config)

    response = synchronizer.sync(data)

    return flask.jsonify(response)


def _generte_sync_configuration():
    return sync.Configuration(
        on_prem_url=os.environ.get('URL_ON_PREMISES'),
        cloud_url=os.environ.get('URL_CLOUD'),
        user_on_prem=os.environ.get('USER_ON_PREMISES'),
    )
