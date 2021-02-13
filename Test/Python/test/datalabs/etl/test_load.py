""" source: datalabs.etl.load """
import pytest

from datalabs.etl.load import LoaderTask
from datalabs.etl.task import ETLComponentParameters


# pylint: disable=redefined-outer-name
def test_loader_task(loader):
    loader.run()

    assert loader.data


@pytest.fixture
def loader():
    return Loader(ETLComponentParameters(variables={}, data=True))


class Loader(LoaderTask):
    def _load(self):
        pass
