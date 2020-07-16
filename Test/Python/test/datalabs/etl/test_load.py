""" REPLACE WITH DOCSTRING """
import pytest

from datalabs.etl.load import LoaderTask


def test_loader_task(loader):
    loader.run()

    assert loader.data == True


@pytest.fixture
def loader():
    return Loader(dict(data=True))


class Loader(LoaderTask):
    def _load(self, data):
        pass
