""" source: datalabs.access.database """
import logging
import tempfile

import pytest
import sqlalchemy as sa
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.database import Database

# pylint: disable=wrong-import-order
from   test.datalabs.access.model import Base, Foo, Bar, Poof

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture
def file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as database_file:
        yield database_file.name


# pylint: disable=redefined-outer-name
@pytest.fixture
def parameters(file):
    return dict(
        backend='sqlite',
        name=file,
        host='',
        port='',
        username='',
        password=''
    )


# pylint: disable=redefined-outer-name, protected-access
@pytest.fixture
def database(parameters):
    class SQLAlchemyDatabase(Database):
        def connect(self):
            engine = sa.create_engine(self.url, echo=True)
            Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

            self._connection = Session()

        def add(self, model, **kwargs):
            self._connection.add(model, **kwargs)

        def commit(self):
            self._connection.commit()


    database = SQLAlchemyDatabase.from_parameters(parameters)
    with database:
        Base.metadata.create_all(database._connection.get_bind())

        yield database


# pylint: disable=redefined-outer-name
def test_adding_objects(database, file):

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

    engine = sa.create_engine(f'sqlite:///{file}', echo=True)
    Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name
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
