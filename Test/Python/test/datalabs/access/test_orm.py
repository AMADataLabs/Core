""" source: datalabs.access.orm """
import logging

import pytest
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.orm import Database
from   test.datalabs.access.model import Base, Foo, Bar, Poof  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_adding_objects(database):
    models = [
        Foo(this='ping', that='biff'),
        Foo(this='pang', that='baff'),
        Foo(this='pong', that='buff'),
        Bar(one=11, two='swish'),
        Bar(one=42, two='swish'),
        Poof(a=30, b=True),
    ]

    for model in models:
        database.add(model)

    database.commit()

    Session = sessionmaker(bind=database._connection.get_bind())  # pylint: disable=invalid-name
    session = Session()

    foos = session.query(Foo).all()
    LOGGER.debug('Foos: %s', foos)
    assert len(foos) == 3

    bars = session.query(Bar).all()
    LOGGER.debug('Bars: %s', bars)
    assert len(bars) == 2

    poofs = session.query(Poof).all()
    LOGGER.debug('Poofs: %s', poofs)
    assert len(poofs) == 1


# pylint: disable=protected-access
@pytest.fixture
def database(database_parameters):
    with Database.from_parameters(database_parameters) as database:
        Base.metadata.create_all(database._connection.get_bind())

        yield database
