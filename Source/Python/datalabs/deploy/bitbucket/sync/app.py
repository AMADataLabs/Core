import logging
from   pathlib import Path
import subprocess

from flask import Flask, request, session, abort, jsonify

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def start():
    app = Flask(__name__)

    _register_blueprints(app)

    _generate_ssh_key_and_print()

    return app


def _register_blueprints(app):
    import datalabs.deploy.bitbucket.sync.trigger as trigger

    app.register_blueprint(trigger.routes)
    app.register_blueprint(trigger.routes, url_prefix='/trigger')

def _generate_ssh_key_and_print():
    key_path = Path('/root/.ssh/id_rsa')
    command = f'ssh-keygen -q -N  -f {str(key_path)}'

    if not key_path.exists():
        subprocess.call(command.split(' '))

    with open('/root/.ssh/id_rsa.pub') as keyfile:
        LOGGER.info(keyfile.readlines())

if __name__ == '__main__':
    start()