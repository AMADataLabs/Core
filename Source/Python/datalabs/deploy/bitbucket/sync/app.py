""" Main BitBucket sync application module. """

import logging


from flask import Flask

import datalabs.deploy.bitbucket.sync.trigger as trigger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def start():
    app = Flask(__name__)

    _register_blueprints(app)

    return app


def _register_blueprints(app):
    app.register_blueprint(trigger.ROUTES)
    app.register_blueprint(trigger.ROUTES, url_prefix='/trigger')

if __name__ == '__main__':
    start()
