""" Helper functions for deploy the CPT database. """
import os

from   datalabs.deploy import database


def create_unless_exists():
    parameters = dict(
        name=os.environ.get('DATABASE_NAME'),
        backend=os.environ.get('DATABASE_BACKEND'),
        host=os.environ.get('DATABASE_HOST'),
        port=os.environ.get('DATABASE_PORT'),
        username=os.environ.get('DATABASE_USERNAME'),
        password=os.environ.get('DATABASE_PASSWORD')
    )

    if not database.exists(parameters):
        name = parameters['name']
        parameters['name'] = os.environ.get('DATABASE_NAME_ADMIN')

        database.create(parameters, name)
