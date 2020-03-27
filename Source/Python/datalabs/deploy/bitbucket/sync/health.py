""" ButBucket Sync application health checkout route. """
import flask

ROUTES = flask.Blueprint('health', __name__)


@ROUTES.route('/')
def health():
    version = 0.1
    return f'Healthy! Running version: {version}'
