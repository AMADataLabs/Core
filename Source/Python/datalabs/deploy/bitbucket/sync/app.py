""" Main BitBucket sync application module. """

import logging
import os
from   pathlib import Path
import subprocess

from flask import Flask

import datalabs.deploy.bitbucket.sync.trigger as trigger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def start():
    app = Flask(__name__)

    _register_blueprints(app)

    _save_ssh_key()

    return app


def _register_blueprints(app):
    app.register_blueprint(trigger.ROUTES)
    app.register_blueprint(trigger.ROUTES, url_prefix='/trigger')


def _save_ssh_key():
    key_path = Path('/BitBucketSync/.ssh/id_rsa')

    with open('/BitBucketSync/.ssh/id_rsa', 'w') as keyfile:
        keyfile.write(os.environ['BITBUCKET_SSH_KEY'])

if __name__ == '__main__':
    start()
