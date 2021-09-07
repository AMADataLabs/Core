""" Database deployment helper functions. """
import os

from sqlalchemy.exc import OperationalError, ProgrammingError

from datalabs.access.orm import Database


def create_unless_exists():
    parameters = dict(
        name=os.environ.get('DATABASE_NAME'),
        backend=os.environ.get('DATABASE_BACKEND'),
        host=os.environ.get('DATABASE_HOST'),
        port=os.environ.get('DATABASE_PORT'),
        username=os.environ.get('DATABASE_USERNAME'),
        password=os.environ.get('DATABASE_PASSWORD')
    )

    if not exists(parameters):
        name = parameters['name']
        parameters['name'] = os.environ.get('DATABASE_NAME_ADMIN')

        create(parameters, name)


# pylint: disable=redefined-outer-name
def exists(parameters):
    exists = None

    try:
        with Database.from_parameters(parameters) as database:
            database.execute('select * from undefined_table;')
    except OperationalError:
        exists = False
    except ProgrammingError:
        exists = True

    return exists


def create(parameters, name):
    with Database.from_parameters(parameters) as database:
        database.execute("commit")
        database.execute(f'create database {name}')
