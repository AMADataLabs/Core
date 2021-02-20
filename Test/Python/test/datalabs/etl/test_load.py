""" source: datalabs.etl.load """
import pytest

from datalabs.etl.load import LoaderTask


# pylint: disable=redefined-outer-name
def test_loader_task(loader):
    loader.run()

    assert loader.data


@pytest.fixture
def loader():
    return Loader(dict(data=True))


class Loader(LoaderTask):
    def _load(self):
        pass
