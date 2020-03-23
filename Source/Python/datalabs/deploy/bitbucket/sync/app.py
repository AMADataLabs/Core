from flask import Flask, request, session, abort, jsonify


def start():
    app = Flask(__name__)

    register_blueprints(app)

    return app


def register_blueprints(app):
    import datalabs.deploy.bitbucket.sync.trigger as trigger

    app.register_blueprint(trigger.routes)
    app.register_blueprint(trigger.routes, url_prefix='/trigger')

if __name__ == '__main__':
    start()