""" source: datalabs.etl.orm.load """
import logging

import mock
import pytest

from   datalabs.etl.orm.load import ORMLoaderTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="Need data from database")
# pylint: disable=redefined-outer-name, protected-access
def test_orm_loader(loader_parameters):
    with mock.patch('datalabs.etl.orm.load.Database'):
        loader = ORMLoaderTask(loader_parameters)
        loader.run()


# pylint: disable=protected-access
def test_get_schema_from_dict_table_args():
    class MockObject:
        __table_args__ = {"schema": "ormloader"}

    schema = ORMLoaderTask._get_schema(MockObject)

    assert schema == "ormloader"


# pylint: disable=protected-access
def test_get_schema_from_tuple_table_args():
    class MockObject:
        __table_args__ = (42, {"stuff": "jfdi9049d0sjafe"}, {"schema": "ormloader"})

    schema = ORMLoaderTask._get_schema(MockObject)

    assert schema == "ormloader"


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def loader_parameters(database, file, data):
    return dict(
        # TASK_CLASS='datalabs.etl.orm.loader.ORMLoaderTask',
        MODEL_CLASSES='test.datalabs.access.model.Foo,'
                      'test.datalabs.access.model.Bar,'
                      'test.datalabs.access.model.Poof',
        DATABASE_HOST='',
        DATABASE_PORT='',
        DATABASE_BACKEND='sqlite',
        DATABASE_NAME=file,
        DATABASE_USERNAME='',
        DATABASE_PASSWORD='',
        data=data
    )
