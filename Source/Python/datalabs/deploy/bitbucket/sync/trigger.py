import flask

import settings

import datalabs.deploy.bitbucket.sync.sync as sync

routes = flask.Blueprint('trigger', __name__)


@routes.route('/')
def sync_bitbucket():
    data = flask.request.get_json()
    config = _generate_sync_configuration()
    synchronizer = sync.BitBucketSynchronizer(config)

    response = synchronizer.sync(data)

    return flask.jsonify(response)


def _generte_sync_configuration():
    return sync.Configuration(
        project=os.environ.get('PROJECT'),
        repository=os.environ.get('REPOSITORY'),
        authorized_user=os.environ.get('AUTHORIZED_USER')
    )
