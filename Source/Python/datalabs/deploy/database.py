from sqlalchemy.exc import OperationalError, ProgrammingError

from datalabs.access.orm import Database


def exists(parameters):
    exists = None

    try:
        with Database.from_parameters(parameters) as db:
            db.execute('select * from undefined_table;')
    except OperationalError:
        exists = False
    except ProgrammingError:
        exists = True

    return exists


def create(parameters, name):
    with Database.from_parameters(parameters) as db:
        db.execute("commit")
        db.execute(f'create database {name}')
