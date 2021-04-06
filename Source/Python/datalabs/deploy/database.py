""" Database deployment helper functions. """
from sqlalchemy.exc import OperationalError, ProgrammingError

from datalabs.access.orm import Database


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
