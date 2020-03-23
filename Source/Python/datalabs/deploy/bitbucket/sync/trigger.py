import os

from flask import Blueprint

routes = Blueprint('trigger', __name__)


@routes.route('/')
def sync_bitbucket():
    return flask.jsonify({'Synced': True})
