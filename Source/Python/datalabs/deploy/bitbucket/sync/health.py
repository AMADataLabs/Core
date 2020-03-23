import os

from flask import Blueprint

routes = Blueprint('health', __name__)


@routes.route('/')
def health():
    # version = os.getenv('GIT_SHORT_HASH', 'LOCAL')
    version = 0.1
    return f'Healthy! Running version: {version}'
