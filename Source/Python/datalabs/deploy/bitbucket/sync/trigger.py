import os

import flask

routes = flask.Blueprint('trigger', __name__)


@routes.route('/')
def sync_bitbucket():
    return flask.jsonify({'Synced': True})
